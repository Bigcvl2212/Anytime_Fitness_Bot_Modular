"""
ClubOS Calendar Management - Part 2
Event Creation, Updates, and Attendee Management
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from clubos_calendar_client import ClubOSCalendarClient, CalendarEvent, TimeSlot


class ClubOSCalendarManager(ClubOSCalendarClient):
    """Extended calendar client with full CRUD operations"""
    
    # ========================================
    # CREATE EVENTS
    # ========================================
    
    def create_event(self, date: str, start_time: str, end_time: str, 
                    event_type: str = 'personal_training', trainer_id: str = None,
                    member_id: str = None, title: str = None) -> Optional[str]:
        """
        Create a new calendar event/appointment.
        
        Args:
            date: Date in YYYY-MM-DD format
            start_time: Start time (e.g., "09:00" or "9:00 AM")
            end_time: End time (e.g., "10:00" or "10:00 AM")
            event_type: Type of event (personal_training, small_group, etc.)
            trainer_id: ID of the trainer
            member_id: ID of the member (optional)
            title: Custom title for the event
            
        Returns:
            Event ID if successful, None otherwise
        """
        if not self.ensure_authenticated():
            return None
        
        print(f"➕ Creating calendar event: {date} {start_time}-{end_time}")
        
        try:
            # Prepare event data
            event_data = {
                'date': date,
                'startTime': start_time,
                'endTime': end_time,
                'eventType': event_type,
                'title': title or f"{event_type.replace('_', ' ').title()} Session"
            }
            
            if trainer_id:
                event_data['trainerId'] = trainer_id
            if member_id:
                event_data['memberId'] = member_id
            
            # Get event type details
            if event_type in self.event_types:
                event_data['eventTypeId'] = self.event_types[event_type]['id']
            
            # Try multiple creation endpoints
            creation_endpoints = [
                '/api/calendar/create',
                '/api/calendar/book',
                '/ajax/calendar/create',
                '/action/Calendar/create',
                '/action/Session/create'
            ]
            
            for endpoint in creation_endpoints:
                event_id = self._attempt_event_creation(endpoint, event_data)
                if event_id:
                    print(f"✅ Event created successfully! ID: {event_id}")
                    return event_id
            
            print("❌ Failed to create event with any endpoint")
            return None
            
        except Exception as e:
            print(f"❌ Error creating event: {e}")
            return None
    
    def _attempt_event_creation(self, endpoint: str, event_data: Dict) -> Optional[str]:
        """Attempt to create an event using a specific endpoint"""
        try:
            url = f"{self.client.base_url}{endpoint}"
            
            # Try POST request
            response = self.client.session.post(
                url,
                json=event_data,
                headers=self.client._get_request_headers("application/json")
            )
            
            if response.ok:
                try:
                    result = response.json()
                    # Extract event ID from response
                    event_id = (result.get('id') or 
                              result.get('eventId') or 
                              result.get('sessionId') or
                              result.get('data', {}).get('id'))
                    return str(event_id) if event_id else None
                except:
                    # If not JSON, check if response contains ID
                    if 'id' in response.text or 'success' in response.text.lower():
                        return "created"  # Generic success indicator
            
            # Try as form data if JSON failed
            response = self.client.session.post(
                url,
                data=event_data,
                headers=self.client._get_request_headers()
            )
            
            if response.ok:
                if 'success' in response.text.lower() or 'created' in response.text.lower():
                    return "created"
            
            return None
            
        except Exception as e:
            print(f"❌ Creation attempt failed for {endpoint}: {e}")
            return None
    
    # ========================================
    # UPDATE EVENTS
    # ========================================
    
    def update_event(self, event_id: str, **updates) -> bool:
        """
        Update an existing calendar event.
        
        Args:
            event_id: ID of the event to update
            **updates: Fields to update (date, start_time, end_time, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.ensure_authenticated():
            return False
        
        print(f"✏️ Updating event {event_id}")
        
        try:
            # Prepare update data
            update_data = {'id': event_id}
            update_data.update(updates)
            
            # Try update endpoints
            update_endpoints = [
                f'/api/calendar/update/{event_id}',
                f'/api/calendar/events/{event_id}',
                '/api/calendar/update',
                '/ajax/calendar/update',
                '/action/Calendar/update'
            ]
            
            for endpoint in update_endpoints:
                success = self._attempt_event_update(endpoint, update_data)
                if success:
                    print(f"✅ Event {event_id} updated successfully!")
                    return True
            
            print(f"❌ Failed to update event {event_id}")
            return False
            
        except Exception as e:
            print(f"❌ Error updating event: {e}")
            return False
    
    def _attempt_event_update(self, endpoint: str, update_data: Dict) -> bool:
        """Attempt to update an event using a specific endpoint"""
        try:
            url = f"{self.client.base_url}{endpoint}"
            
            # Try PUT request
            response = self.client.session.put(
                url,
                json=update_data,
                headers=self.client._get_request_headers("application/json")
            )
            
            if response.ok:
                return True
            
            # Try POST request
            response = self.client.session.post(
                url,
                json=update_data,
                headers=self.client._get_request_headers("application/json")
            )
            
            if response.ok:
                return True
            
            # Try as form data
            response = self.client.session.post(
                url,
                data=update_data,
                headers=self.client._get_request_headers()
            )
            
            return response.ok
            
        except Exception as e:
            print(f"❌ Update attempt failed for {endpoint}: {e}")
            return False
    
    # ========================================
    # DELETE EVENTS
    # ========================================
    
    def delete_event(self, event_id: str) -> bool:
        """
        Delete a calendar event.
        
        Args:
            event_id: ID of the event to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.ensure_authenticated():
            return False
        
        print(f"🗑️ Deleting event {event_id}")
        
        try:
            # Try delete endpoints
            delete_endpoints = [
                f'/api/calendar/delete/{event_id}',
                f'/api/calendar/events/{event_id}',
                f'/api/calendar/cancel/{event_id}',
                '/api/calendar/delete',
                '/ajax/calendar/delete',
                '/action/Calendar/delete'
            ]
            
            for endpoint in delete_endpoints:
                success = self._attempt_event_deletion(endpoint, event_id)
                if success:
                    print(f"✅ Event {event_id} deleted successfully!")
                    return True
            
            print(f"❌ Failed to delete event {event_id}")
            return False
            
        except Exception as e:
            print(f"❌ Error deleting event: {e}")
            return False
    
    def _attempt_event_deletion(self, endpoint: str, event_id: str) -> bool:
        """Attempt to delete an event using a specific endpoint"""
        try:
            url = f"{self.client.base_url}{endpoint}"
            
            # Try DELETE request
            if not endpoint.endswith(event_id):
                # If event ID not in URL, send as parameter
                response = self.client.session.delete(
                    url,
                    json={'id': event_id},
                    headers=self.client._get_request_headers("application/json")
                )
            else:
                response = self.client.session.delete(
                    url,
                    headers=self.client._get_request_headers("application/json")
                )
            
            if response.ok:
                return True
            
            # Try POST with delete action
            response = self.client.session.post(
                url,
                json={'id': event_id, 'action': 'delete'},
                headers=self.client._get_request_headers("application/json")
            )
            
            if response.ok:
                return True
            
            # Try as form data
            response = self.client.session.post(
                url,
                data={'id': event_id, 'action': 'delete'},
                headers=self.client._get_request_headers()
            )
            
            return response.ok
            
        except Exception as e:
            print(f"❌ Delete attempt failed for {endpoint}: {e}")
            return False
    
    # ========================================
    # ATTENDEE MANAGEMENT
    # ========================================
    
    def add_attendee_to_event(self, event_id: str, member_id: str) -> bool:
        """
        Add a member to a calendar event.
        
        Args:
            event_id: ID of the event
            member_id: ID of the member to add
            
        Returns:
            True if successful, False otherwise
        """
        if not self.ensure_authenticated():
            return False
        
        print(f"👤➕ Adding member {member_id} to event {event_id}")
        
        try:
            attendee_data = {
                'eventId': event_id,
                'memberId': member_id
            }
            
            # Try attendee addition endpoints
            add_endpoints = [
                '/api/calendar/attendee/add',
                '/api/calendar/addAttendee',
                '/ajax/calendar/attendee/add',
                '/action/Calendar/addAttendee'
            ]
            
            for endpoint in add_endpoints:
                success = self._attempt_attendee_action(endpoint, attendee_data)
                if success:
                    print(f"✅ Member {member_id} added to event {event_id}")
                    return True
            
            print(f"❌ Failed to add member {member_id} to event {event_id}")
            return False
            
        except Exception as e:
            print(f"❌ Error adding attendee: {e}")
            return False
    
    def remove_attendee_from_event(self, event_id: str, member_id: str) -> bool:
        """
        Remove a member from a calendar event.
        
        Args:
            event_id: ID of the event
            member_id: ID of the member to remove
            
        Returns:
            True if successful, False otherwise
        """
        if not self.ensure_authenticated():
            return False
        
        print(f"👤➖ Removing member {member_id} from event {event_id}")
        
        try:
            attendee_data = {
                'eventId': event_id,
                'memberId': member_id
            }
            
            # Try attendee removal endpoints
            remove_endpoints = [
                '/api/calendar/attendee/remove',
                '/api/calendar/removeAttendee',
                '/ajax/calendar/attendee/remove',
                '/action/Calendar/removeAttendee'
            ]
            
            for endpoint in remove_endpoints:
                success = self._attempt_attendee_action(endpoint, attendee_data)
                if success:
                    print(f"✅ Member {member_id} removed from event {event_id}")
                    return True
            
            print(f"❌ Failed to remove member {member_id} from event {event_id}")
            return False
            
        except Exception as e:
            print(f"❌ Error removing attendee: {e}")
            return False
    
    def _attempt_attendee_action(self, endpoint: str, attendee_data: Dict) -> bool:
        """Attempt an attendee action using a specific endpoint"""
        try:
            url = f"{self.client.base_url}{endpoint}"
            
            # Try POST request with JSON
            response = self.client.session.post(
                url,
                json=attendee_data,
                headers=self.client._get_request_headers("application/json")
            )
            
            if response.ok:
                return True
            
            # Try POST request with form data
            response = self.client.session.post(
                url,
                data=attendee_data,
                headers=self.client._get_request_headers()
            )
            
            return response.ok
            
        except Exception as e:
            print(f"❌ Attendee action failed for {endpoint}: {e}")
            return False
    
    # ========================================
    # CONVENIENCE METHODS
    # ========================================
    
    def reschedule_event(self, event_id: str, new_date: str, new_start_time: str, 
                        new_end_time: str = None) -> bool:
        """
        Reschedule an event to a new date and time.
        
        Args:
            event_id: ID of the event to reschedule
            new_date: New date in YYYY-MM-DD format
            new_start_time: New start time
            new_end_time: New end time (optional)
            
        Returns:
            True if successful, False otherwise
        """
        updates = {
            'date': new_date,
            'startTime': new_start_time
        }
        
        if new_end_time:
            updates['endTime'] = new_end_time
        
        return self.update_event(event_id, **updates)
    
    def get_event_attendees(self, event_id: str) -> List[Dict]:
        """
        Get list of attendees for an event.
        
        Args:
            event_id: ID of the event
            
        Returns:
            List of attendee dictionaries
        """
        if not self.ensure_authenticated():
            return []
        
        try:
            attendees_url = f"{self.client.base_url}/api/calendar/events/{event_id}/attendees"
            response = self.client.session.get(
                attendees_url,
                headers=self.client._get_request_headers("application/json")
            )
            
            if response.ok:
                try:
                    data = response.json()
                    if isinstance(data, dict) and 'attendees' in data:
                        return data['attendees']
                    elif isinstance(data, list):
                        return data
                except:
                    pass
            
            return []
            
        except Exception as e:
            print(f"❌ Error getting event attendees: {e}")
            return []


def create_calendar_manager(username: str = None, password: str = None) -> ClubOSCalendarManager:
    """Factory function to create and authenticate a calendar manager"""
    manager = ClubOSCalendarManager(username, password)
    manager.authenticate()
    return manager


# Example usage and testing
if __name__ == "__main__":
    # Initialize calendar manager
    calendar_manager = create_calendar_manager()
    
    if calendar_manager.is_authenticated:
        print("🎉 Calendar manager ready for testing!")
        
        # Test creating an event
        print("\\n➕ Testing event creation...")
        event_id = calendar_manager.create_event(
            date="2025-01-20",
            start_time="10:00",
            end_time="11:00",
            event_type="personal_training"
        )
        
        if event_id:
            print(f"Created event with ID: {event_id}")
            
            # Test updating the event
            print("\\n✏️ Testing event update...")
            updated = calendar_manager.update_event(
                event_id,
                title="Updated Training Session"
            )
            print(f"Update result: {updated}")
            
            # Test adding attendee (if we have a member ID)
            # print("\\n👤 Testing add attendee...")
            # added = calendar_manager.add_attendee_to_event(event_id, "member_123")
            # print(f"Add attendee result: {added}")
        
    else:
        print("❌ Calendar manager authentication failed")
