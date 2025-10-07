#!/usr/bin/env python3
"""
Inbox WebSocket Route
Provides real-time inbox updates via WebSocket connection
"""

import logging
import json
from flask import Blueprint, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from typing import Dict, List

logger = logging.getLogger(__name__)

# Global SocketIO instance (will be initialized by main app)
socketio = None

# Blueprint for inbox websocket routes
inbox_ws_bp = Blueprint('inbox_websocket', __name__)

# Track connected clients
connected_clients = {}

def init_websocket(app, socketio_instance):
    """
    Initialize WebSocket handlers

    Args:
        app: Flask application
        socketio_instance: Flask-SocketIO instance
    """
    global socketio
    socketio = socketio_instance
    logger.info("✅ Inbox WebSocket initialized")


@inbox_ws_bp.route('/inbox/ws/status')
def websocket_status():
    """Get WebSocket connection status"""
    return {
        'status': 'active',
        'connected_clients': len(connected_clients),
        'clients': list(connected_clients.keys())
    }


# WebSocket event handlers
def register_websocket_handlers(socketio_instance):
    """
    Register WebSocket event handlers

    Args:
        socketio_instance: Flask-SocketIO instance
    """
    global socketio
    socketio = socketio_instance

    @socketio.on('connect', namespace='/inbox')
    def handle_connect():
        """Handle client connection"""
        client_id = request.sid
        logger.info(f"📱 Client connected: {client_id}")

        # Store client info
        connected_clients[client_id] = {
            'sid': client_id,
            'connected_at': None,
            'owner_id': None,
            'subscribed_rooms': []
        }

        # Send connection confirmation
        emit('connected', {
            'client_id': client_id,
            'status': 'connected',
            'message': 'Connected to inbox real-time updates'
        })

    @socketio.on('disconnect', namespace='/inbox')
    def handle_disconnect():
        """Handle client disconnection"""
        client_id = request.sid
        logger.info(f"📴 Client disconnected: {client_id}")

        # Remove client info
        if client_id in connected_clients:
            del connected_clients[client_id]

    @socketio.on('subscribe', namespace='/inbox')
    def handle_subscribe(data):
        """
        Handle subscription to inbox updates

        Data format:
        {
            "owner_id": "user_id_here",
            "conversation_ids": ["conv1", "conv2"]  # Optional
        }
        """
        client_id = request.sid
        owner_id = data.get('owner_id')
        conversation_ids = data.get('conversation_ids', [])

        logger.info(f"📡 Client {client_id} subscribing to owner_id: {owner_id}")

        # Join owner-specific room
        if owner_id:
            room_name = f"owner_{owner_id}"
            join_room(room_name)

            # Update client info
            if client_id in connected_clients:
                connected_clients[client_id]['owner_id'] = owner_id
                connected_clients[client_id]['subscribed_rooms'].append(room_name)

            logger.info(f"✅ Client {client_id} joined room: {room_name}")

        # Join conversation-specific rooms
        for conv_id in conversation_ids:
            conv_room = f"conversation_{conv_id}"
            join_room(conv_room)

            if client_id in connected_clients:
                connected_clients[client_id]['subscribed_rooms'].append(conv_room)

            logger.info(f"✅ Client {client_id} joined conversation: {conv_id}")

        # Send subscription confirmation
        emit('subscribed', {
            'owner_id': owner_id,
            'conversation_ids': conversation_ids,
            'status': 'subscribed'
        })

    @socketio.on('unsubscribe', namespace='/inbox')
    def handle_unsubscribe(data):
        """Handle unsubscription from inbox updates"""
        client_id = request.sid
        owner_id = data.get('owner_id')

        if owner_id:
            room_name = f"owner_{owner_id}"
            leave_room(room_name)
            logger.info(f"📴 Client {client_id} left room: {room_name}")

        emit('unsubscribed', {'status': 'unsubscribed'})

    @socketio.on('request_sync', namespace='/inbox')
    def handle_request_sync(data):
        """
        Handle manual sync request from client

        Data format:
        {
            "owner_id": "user_id_here"
        }
        """
        client_id = request.sid
        owner_id = data.get('owner_id')

        logger.info(f"🔄 Client {client_id} requesting sync for owner: {owner_id}")

        # Emit sync request event that the poller can listen to
        emit('sync_requested', {
            'client_id': client_id,
            'owner_id': owner_id,
            'status': 'processing'
        })

    @socketio.on('mark_read', namespace='/inbox')
    def handle_mark_read(data):
        """
        Handle mark message as read request

        Data format:
        {
            "message_id": "msg_id_here",
            "conversation_id": "conv_id_here"
        }
        """
        message_id = data.get('message_id')
        conversation_id = data.get('conversation_id')

        logger.info(f"✅ Marking message {message_id} as read")

        # Emit to conversation room
        if conversation_id:
            room_name = f"conversation_{conversation_id}"
            emit('message_read', {
                'message_id': message_id,
                'conversation_id': conversation_id,
                'read_at': None
            }, room=room_name)


# Broadcast functions for the polling service to use
def broadcast_new_messages(messages: List[Dict], owner_id: str = None):
    """
    Broadcast new messages to subscribed clients

    Args:
        messages: List of new message dictionaries
        owner_id: Optional owner ID to target specific room
    """
    if not socketio:
        logger.warning("⚠️ SocketIO not initialized, cannot broadcast messages")
        return

    try:
        # Determine target room
        room = f"owner_{owner_id}" if owner_id else None

        # Broadcast to appropriate room
        logger.info(f"📢 Broadcasting {len(messages)} new messages to room: {room or 'all'}")

        socketio.emit('new_messages', {
            'messages': messages,
            'count': len(messages),
            'timestamp': None
        }, namespace='/inbox', room=room)

    except Exception as e:
        logger.error(f"❌ Error broadcasting new messages: {e}")


def broadcast_poll_update(poll_stats: Dict, owner_id: str = None):
    """
    Broadcast poll update to subscribed clients

    Args:
        poll_stats: Poll statistics dictionary
        owner_id: Optional owner ID
    """
    if not socketio:
        return

    try:
        room = f"owner_{owner_id}" if owner_id else None

        socketio.emit('poll_update', {
            'stats': poll_stats,
            'timestamp': poll_stats.get('timestamp')
        }, namespace='/inbox', room=room)

    except Exception as e:
        logger.error(f"❌ Error broadcasting poll update: {e}")


def broadcast_error(error_message: str, owner_id: str = None):
    """
    Broadcast error to subscribed clients

    Args:
        error_message: Error message
        owner_id: Optional owner ID
    """
    if not socketio:
        return

    try:
        room = f"owner_{owner_id}" if owner_id else None

        socketio.emit('error', {
            'error': error_message,
            'timestamp': None
        }, namespace='/inbox', room=room)

    except Exception as e:
        logger.error(f"❌ Error broadcasting error: {e}")


def notify_ai_response(original_message_id: str, ai_response: str,
                       conversation_id: str = None, member_id: str = None):
    """
    Notify clients when AI generates a response

    Args:
        original_message_id: ID of the message AI is responding to
        ai_response: AI-generated response text
        conversation_id: Conversation ID
        member_id: Member ID
    """
    if not socketio:
        return

    try:
        # Broadcast to conversation room
        room = f"conversation_{conversation_id}" if conversation_id else None

        socketio.emit('ai_response', {
            'original_message_id': original_message_id,
            'ai_response': ai_response,
            'conversation_id': conversation_id,
            'member_id': member_id,
            'timestamp': None
        }, namespace='/inbox', room=room)

        logger.info(f"🤖 Broadcast AI response for message {original_message_id}")

    except Exception as e:
        logger.error(f"❌ Error broadcasting AI response: {e}")
