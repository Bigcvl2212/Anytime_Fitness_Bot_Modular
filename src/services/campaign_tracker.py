"""
Real-time Campaign Tracking Service
Provides comprehensive tracking, monitoring, and control for marketing campaigns
"""
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class CampaignStatus(Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"

class CampaignPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class CampaignProgress:
    campaign_id: str
    total_recipients: int
    processed: int
    successful: int
    failed: int
    skipped: int
    current_batch: int
    total_batches: int
    start_time: datetime
    last_update: datetime
    estimated_completion: Optional[datetime]
    current_member: Optional[str]
    error_count: int
    rate_limit_hits: int
    
    @property
    def percentage_complete(self) -> float:
        if self.total_recipients == 0:
            return 0.0
        return (self.processed / self.total_recipients) * 100
    
    @property
    def success_rate(self) -> float:
        if self.processed == 0:
            return 0.0
        return (self.successful / self.processed) * 100
    
    @property
    def messages_per_minute(self) -> float:
        if not self.start_time:
            return 0.0
        elapsed = (datetime.now() - self.start_time).total_seconds() / 60
        if elapsed == 0:
            return 0.0
        return self.processed / elapsed

@dataclass
class CampaignMetadata:
    campaign_id: str
    name: str
    message_text: str
    message_type: str
    subject: Optional[str]
    categories: List[str]
    status: CampaignStatus
    priority: CampaignPriority
    created_at: datetime
    created_by: str
    max_recipients: int
    batch_size: int
    delay_between_batches: int
    retry_attempts: int
    notes: str

class CampaignTracker:
    """Real-time campaign tracking and management service"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.active_campaigns: Dict[str, CampaignProgress] = {}
        self.campaign_metadata: Dict[str, CampaignMetadata] = {}
        self.campaign_locks: Dict[str, threading.Lock] = {}
        self.monitoring_thread = None
        self.is_monitoring = False
        self._initialize_database()
        
    def _initialize_database(self):
        """Initialize campaign tracking tables"""
        try:
            # Enhanced campaigns table
            self.db_manager.execute_query('''
                CREATE TABLE IF NOT EXISTS campaigns_v2 (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    message_text TEXT NOT NULL,
                    message_type TEXT DEFAULT 'sms',
                    subject TEXT,
                    categories TEXT NOT NULL,
                    status TEXT DEFAULT 'draft',
                    priority TEXT DEFAULT 'normal',
                    total_recipients INTEGER DEFAULT 0,
                    max_recipients INTEGER DEFAULT 999999,
                    batch_size INTEGER DEFAULT 50,
                    delay_between_batches INTEGER DEFAULT 30,
                    retry_attempts INTEGER DEFAULT 3,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    notes TEXT
                )
            ''')
            
            # Real-time progress tracking
            self.db_manager.execute_query('''
                CREATE TABLE IF NOT EXISTS campaign_progress_v2 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id TEXT NOT NULL,
                    processed INTEGER DEFAULT 0,
                    successful INTEGER DEFAULT 0,
                    failed INTEGER DEFAULT 0,
                    skipped INTEGER DEFAULT 0,
                    current_batch INTEGER DEFAULT 0,
                    total_batches INTEGER DEFAULT 0,
                    current_member TEXT,
                    error_count INTEGER DEFAULT 0,
                    rate_limit_hits INTEGER DEFAULT 0,
                    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    estimated_completion TIMESTAMP,
                    FOREIGN KEY (campaign_id) REFERENCES campaigns_v2(id)
                )
            ''')
            
            # Detailed message logs
            self.db_manager.execute_query('''
                CREATE TABLE IF NOT EXISTS campaign_message_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id TEXT NOT NULL,
                    member_id TEXT,
                    member_name TEXT,
                    member_contact TEXT,
                    status TEXT, -- sent, failed, skipped
                    error_message TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    batch_number INTEGER,
                    retry_count INTEGER DEFAULT 0,
                    FOREIGN KEY (campaign_id) REFERENCES campaigns_v2(id)
                )
            ''')
            
            # Campaign events log
            self.db_manager.execute_query('''
                CREATE TABLE IF NOT EXISTS campaign_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id TEXT NOT NULL,
                    event_type TEXT NOT NULL, -- started, paused, resumed, completed, error
                    event_message TEXT,
                    event_data TEXT, -- JSON data
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (campaign_id) REFERENCES campaigns_v2(id)
                )
            ''')
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize campaign tracking database: {e}")
    
    def create_campaign(self, metadata: CampaignMetadata) -> str:
        """Create a new campaign and return its ID"""
        try:
            # Store campaign metadata
            self.db_manager.execute_query('''
                INSERT INTO campaigns_v2 
                (id, name, message_text, message_type, subject, categories, status, priority,
                 max_recipients, batch_size, delay_between_batches, retry_attempts, created_by, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metadata.campaign_id,
                metadata.name,
                metadata.message_text,
                metadata.message_type,
                metadata.subject,
                ','.join(metadata.categories),
                metadata.status.value,
                metadata.priority.value,
                metadata.max_recipients,
                metadata.batch_size,
                metadata.delay_between_batches,
                metadata.retry_attempts,
                metadata.created_by,
                metadata.notes
            ))
            
            # Store in memory
            self.campaign_metadata[metadata.campaign_id] = metadata
            self.campaign_locks[metadata.campaign_id] = threading.Lock()
            
            # Log event
            self._log_campaign_event(metadata.campaign_id, "created", f"Campaign '{metadata.name}' created")
            
            logger.info(f"📊 Created campaign: {metadata.campaign_id} - {metadata.name}")
            return metadata.campaign_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create campaign {metadata.campaign_id}: {e}")
            raise
    
    def start_campaign(self, campaign_id: str, total_recipients: int) -> bool:
        """Start a campaign and initialize progress tracking"""
        try:
            with self.campaign_locks.get(campaign_id, threading.Lock()):
                # Update campaign status
                self.db_manager.execute_query('''
                    UPDATE campaigns_v2 
                    SET status = 'running', started_at = CURRENT_TIMESTAMP, total_recipients = ?
                    WHERE id = ?
                ''', (total_recipients, campaign_id))
                
                # Initialize progress tracking
                progress = CampaignProgress(
                    campaign_id=campaign_id,
                    total_recipients=total_recipients,
                    processed=0,
                    successful=0,
                    failed=0,
                    skipped=0,
                    current_batch=1,
                    total_batches=max(1, (total_recipients // 50) + (1 if total_recipients % 50 else 0)),
                    start_time=datetime.now(),
                    last_update=datetime.now(),
                    estimated_completion=None,
                    current_member=None,
                    error_count=0,
                    rate_limit_hits=0
                )
                
                self.active_campaigns[campaign_id] = progress
                
                # Store initial progress
                self._save_progress(progress)
                
                # Log event
                self._log_campaign_event(campaign_id, "started", f"Campaign started with {total_recipients} recipients")
                
                # Start monitoring if not already running
                if not self.is_monitoring:
                    self._start_monitoring()
                
                logger.info(f"🚀 Started campaign: {campaign_id} with {total_recipients} recipients")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to start campaign {campaign_id}: {e}")
            return False
    
    def update_progress(self, campaign_id: str, processed: int = 0, successful: int = 0, 
                       failed: int = 0, skipped: int = 0, current_member: str = None,
                       error_message: str = None) -> bool:
        """Update campaign progress in real-time"""
        try:
            if campaign_id not in self.active_campaigns:
                return False
                
            with self.campaign_locks.get(campaign_id, threading.Lock()):
                progress = self.active_campaigns[campaign_id]
                
                # Update counters
                if processed > 0:
                    progress.processed += processed
                if successful > 0:
                    progress.successful += successful
                if failed > 0:
                    progress.failed += failed
                    progress.error_count += failed
                if skipped > 0:
                    progress.skipped += skipped
                
                # Update current state
                progress.last_update = datetime.now()
                if current_member:
                    progress.current_member = current_member
                
                # Calculate estimated completion
                if progress.processed > 0 and progress.total_recipients > progress.processed:
                    rate = progress.messages_per_minute
                    if rate > 0:
                        remaining = progress.total_recipients - progress.processed
                        minutes_left = remaining / rate
                        progress.estimated_completion = datetime.now() + timedelta(minutes=minutes_left)
                
                # Save to database
                self._save_progress(progress)
                
                # Log individual message if there's an error
                if error_message:
                    self._log_message_result(campaign_id, current_member, "failed", error_message)
                elif successful > 0:
                    self._log_message_result(campaign_id, current_member, "sent")
                
                # Check if campaign is complete
                if progress.processed >= progress.total_recipients:
                    self._complete_campaign(campaign_id)
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to update progress for campaign {campaign_id}: {e}")
            return False
    
    def pause_campaign(self, campaign_id: str) -> bool:
        """Pause a running campaign"""
        try:
            self.db_manager.execute_query('''
                UPDATE campaigns_v2 SET status = 'paused' WHERE id = ?
            ''', (campaign_id,))
            
            if campaign_id in self.campaign_metadata:
                self.campaign_metadata[campaign_id].status = CampaignStatus.PAUSED
            
            self._log_campaign_event(campaign_id, "paused", "Campaign paused by user")
            logger.info(f"⏸️ Paused campaign: {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to pause campaign {campaign_id}: {e}")
            return False
    
    def resume_campaign(self, campaign_id: str) -> bool:
        """Resume a paused campaign"""
        try:
            self.db_manager.execute_query('''
                UPDATE campaigns_v2 SET status = 'running' WHERE id = ?
            ''', (campaign_id,))
            
            if campaign_id in self.campaign_metadata:
                self.campaign_metadata[campaign_id].status = CampaignStatus.RUNNING
            
            self._log_campaign_event(campaign_id, "resumed", "Campaign resumed by user")
            logger.info(f"▶️ Resumed campaign: {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to resume campaign {campaign_id}: {e}")
            return False
    
    def cancel_campaign(self, campaign_id: str) -> bool:
        """Cancel a campaign"""
        try:
            self.db_manager.execute_query('''
                UPDATE campaigns_v2 SET status = 'cancelled', completed_at = CURRENT_TIMESTAMP WHERE id = ?
            ''', (campaign_id,))
            
            if campaign_id in self.campaign_metadata:
                self.campaign_metadata[campaign_id].status = CampaignStatus.CANCELLED
            
            if campaign_id in self.active_campaigns:
                del self.active_campaigns[campaign_id]
            
            self._log_campaign_event(campaign_id, "cancelled", "Campaign cancelled by user")
            logger.info(f"🛑 Cancelled campaign: {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to cancel campaign {campaign_id}: {e}")
            return False
    
    def complete_campaign(self, campaign_id: str, final_successful: int = 0, final_failed: int = 0, final_errors: List[str] = None) -> bool:
        """Complete a campaign with final statistics"""
        try:
            # Update campaign status to completed
            self.db_manager.execute_query('''
                UPDATE campaigns_v2 SET 
                    status = 'completed', 
                    completed_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (campaign_id,))
            
            # Update final progress statistics
            self.db_manager.execute_query('''
                UPDATE campaign_progress_v2 SET 
                    successful = ?,
                    failed = ?,
                    last_update = CURRENT_TIMESTAMP
                WHERE campaign_id = ?
            ''', (final_successful, final_failed, campaign_id))
            
            # Log completion event
            completion_message = f"Campaign completed: {final_successful} successful, {final_failed} failed"
            self._log_campaign_event(campaign_id, "completed", completion_message)
            
            # Log any final errors
            if final_errors:
                for error in final_errors[:10]:  # Log first 10 errors
                    self._log_campaign_event(campaign_id, "error", f"Final error: {error}")
            
            # Update in-memory cache
            if campaign_id in self.campaign_metadata:
                self.campaign_metadata[campaign_id].status = CampaignStatus.COMPLETED
            
            if campaign_id in self.active_campaigns:
                del self.active_campaigns[campaign_id]
            
            logger.info(f"✅ Completed campaign: {campaign_id} ({final_successful}/{final_successful + final_failed} successful)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to complete campaign {campaign_id}: {e}")
            return False
    
    def get_campaign_status(self, campaign_id: str) -> Dict[str, Any]:
        """Get detailed campaign status and progress"""
        try:
            # Get campaign metadata
            campaign_data = self.db_manager.execute_query('''
                SELECT * FROM campaigns_v2 WHERE id = ?
            ''', (campaign_id,))
            
            if not campaign_data:
                return {'error': 'Campaign not found'}
            
            campaign = campaign_data[0]
            
            # Get progress data
            progress_data = self.db_manager.execute_query('''
                SELECT * FROM campaign_progress_v2 WHERE campaign_id = ? ORDER BY last_update DESC LIMIT 1
            ''', (campaign_id,))
            
            progress = progress_data[0] if progress_data else {}
            
            # Get recent events
            events = self.db_manager.execute_query('''
                SELECT event_type, event_message, timestamp 
                FROM campaign_events 
                WHERE campaign_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 10
            ''', (campaign_id,))
            
            # Calculate real-time stats
            status_info = {
                'campaign_id': campaign_id,
                'name': campaign['name'],
                'status': campaign['status'],
                'priority': campaign['priority'],
                'created_at': campaign['created_at'],
                'started_at': campaign.get('started_at'),
                'completed_at': campaign.get('completed_at'),
                'total_recipients': campaign.get('total_recipients', 0),
                'processed': progress.get('processed', 0),
                'successful': progress.get('successful', 0),
                'failed': progress.get('failed', 0),
                'skipped': progress.get('skipped', 0),
                'error_count': progress.get('error_count', 0),
                'current_member': progress.get('current_member'),
                'last_update': progress.get('last_update'),
                'estimated_completion': progress.get('estimated_completion'),
                'events': events
            }
            
            # Add calculated fields
            if status_info['total_recipients'] > 0:
                status_info['percentage_complete'] = (status_info['processed'] / status_info['total_recipients']) * 100
            else:
                status_info['percentage_complete'] = 0
                
            if status_info['processed'] > 0:
                status_info['success_rate'] = (status_info['successful'] / status_info['processed']) * 100
            else:
                status_info['success_rate'] = 0
            
            return status_info
            
        except Exception as e:
            logger.error(f"❌ Failed to get campaign status for {campaign_id}: {e}")
            return {'error': str(e)}
    
    def get_all_active_campaigns(self) -> List[Dict[str, Any]]:
        """Get status of all active campaigns"""
        try:
            campaigns = self.db_manager.execute_query('''
                SELECT id FROM campaigns_v2 WHERE status IN ('running', 'paused', 'queued')
            ''')
            
            return [self.get_campaign_status(campaign['id']) for campaign in campaigns]
            
        except Exception as e:
            logger.error(f"❌ Failed to get active campaigns: {e}")
            return []
    
    def _complete_campaign(self, campaign_id: str):
        """Mark a campaign as completed"""
        try:
            self.db_manager.execute_query('''
                UPDATE campaigns_v2 SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?
            ''', (campaign_id,))
            
            if campaign_id in self.campaign_metadata:
                self.campaign_metadata[campaign_id].status = CampaignStatus.COMPLETED
            
            if campaign_id in self.active_campaigns:
                progress = self.active_campaigns[campaign_id]
                self._log_campaign_event(
                    campaign_id, 
                    "completed", 
                    f"Campaign completed: {progress.successful}/{progress.total_recipients} successful"
                )
                del self.active_campaigns[campaign_id]
            
            logger.info(f"✅ Completed campaign: {campaign_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to complete campaign {campaign_id}: {e}")
    
    def _save_progress(self, progress: CampaignProgress):
        """Save progress to database"""
        try:
            self.db_manager.execute_query('''
                INSERT OR REPLACE INTO campaign_progress_v2 
                (campaign_id, processed, successful, failed, skipped, current_batch, total_batches,
                 current_member, error_count, rate_limit_hits, last_update, estimated_completion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                progress.campaign_id,
                progress.processed,
                progress.successful,
                progress.failed,
                progress.skipped,
                progress.current_batch,
                progress.total_batches,
                progress.current_member,
                progress.error_count,
                progress.rate_limit_hits,
                progress.last_update.isoformat(),
                progress.estimated_completion.isoformat() if progress.estimated_completion else None
            ))
            
        except Exception as e:
            logger.error(f"❌ Failed to save progress for {progress.campaign_id}: {e}")
    
    def _log_campaign_event(self, campaign_id: str, event_type: str, message: str, data: Dict = None):
        """Log a campaign event"""
        try:
            self.db_manager.execute_query('''
                INSERT INTO campaign_events (campaign_id, event_type, event_message, event_data)
                VALUES (?, ?, ?, ?)
            ''', (campaign_id, event_type, message, json.dumps(data) if data else None))
            
        except Exception as e:
            logger.error(f"❌ Failed to log event for campaign {campaign_id}: {e}")
    
    def _log_message_result(self, campaign_id: str, member_info: str, status: str, error: str = None):
        """Log individual message result"""
        try:
            # Parse member info if it's in format "name <contact>"
            member_name = member_info
            member_contact = ""
            
            if member_info and '<' in member_info:
                parts = member_info.split('<')
                member_name = parts[0].strip()
                member_contact = parts[1].rstrip('>').strip()
            
            self.db_manager.execute_query('''
                INSERT INTO campaign_message_logs 
                (campaign_id, member_name, member_contact, status, error_message)
                VALUES (?, ?, ?, ?, ?)
            ''', (campaign_id, member_name, member_contact, status, error))
            
        except Exception as e:
            logger.error(f"❌ Failed to log message result for {campaign_id}: {e}")
    
    def _start_monitoring(self):
        """Start the monitoring thread"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            logger.info("📊 Started campaign monitoring thread")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                # Check for stalled campaigns
                for campaign_id in list(self.active_campaigns.keys()):
                    progress = self.active_campaigns[campaign_id]
                    
                    # Check if campaign has been inactive for too long
                    if datetime.now() - progress.last_update > timedelta(minutes=10):
                        logger.warning(f"⚠️ Campaign {campaign_id} appears stalled")
                        self._log_campaign_event(campaign_id, "warning", "Campaign appears stalled - no updates in 10 minutes")
                
                # Sleep for 30 seconds before next check
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                time.sleep(60)  # Sleep longer on error
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("🛑 Stopped campaign monitoring")

# Global instance
campaign_tracker = None

def get_campaign_tracker(db_manager=None):
    """Get or create the global campaign tracker instance"""
    global campaign_tracker
    if campaign_tracker is None and db_manager:
        campaign_tracker = CampaignTracker(db_manager)
    return campaign_tracker