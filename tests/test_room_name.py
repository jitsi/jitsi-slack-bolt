import pytest
from jitsi_slack_bolt.util.room_name import generate_room_name


class TestRoomNameGenerator:
    """Test the room name generator functionality"""

    def test_generate_room_name(self):
        """Test that room names are generated properly"""
        # Generate a room name
        room_name = generate_room_name()

        # Verify it's a string and not empty
        assert isinstance(room_name, str)
        assert len(room_name) > 0

    def test_multiple_room_names_are_different(self):
        """Test that multiple generated room names are different"""
        # Generate multiple room names
        room_names = [generate_room_name() for _ in range(10)]

        # Check that they're all unique
        assert len(set(room_names)) == 10, "Generated room names should be unique"
