#!/usr/bin/env python3
"""
Test script for DatabaseRegistry functionality
Tests the registry database operations and API endpoints
"""

import os
import sys
import pytest
import tempfile
import shutil
from database import DatabaseRegistry, ReadathonDB

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@pytest.fixture
def client():
    """Create a Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def test_registry():
    """Create a temporary test registry database"""
    test_registry_path = 'db/test_registry.db'

    # Create test registry
    registry = DatabaseRegistry(test_registry_path)

    yield registry

    # Cleanup
    registry.close()
    if os.path.exists(test_registry_path):
        os.remove(test_registry_path)


class TestDatabaseRegistry:
    """Test DatabaseRegistry class methods"""

    def test_registry_initialization(self):
        """Test that registry database initializes correctly"""
        registry = DatabaseRegistry()
        databases = registry.list_databases()

        # Should have at least 2 databases (2025 and Sample)
        assert len(databases) >= 2, "Registry should contain at least 2 databases"

        # Check for expected fields
        for db in databases:
            assert 'db_id' in db
            assert 'db_filename' in db
            assert 'display_name' in db
            assert 'year' in db
            assert 'is_active' in db
            assert 'student_count' in db
            assert 'total_days' in db
            assert 'total_donations' in db

        registry.close()
        print("✓ Registry initializes with correct schema")

    def test_list_databases(self):
        """Test listing all databases from registry"""
        registry = DatabaseRegistry()
        databases = registry.list_databases()

        # Should return a list
        assert isinstance(databases, list)

        # Each entry should be a dict with required fields
        for db in databases:
            assert 'db_id' in db
            assert 'db_filename' in db
            assert 'display_name' in db

        registry.close()
        print("✓ list_databases returns valid structure")

    def test_get_database_by_id(self):
        """Test retrieving a specific database by ID"""
        registry = DatabaseRegistry()
        databases = registry.list_databases()

        if databases:
            test_id = databases[0]['db_id']
            db = registry.get_database(test_id)

            assert db is not None
            assert db['db_id'] == test_id
            assert 'display_name' in db
            assert 'db_filename' in db

        registry.close()
        print("✓ get_database retrieves by ID")

    def test_get_database_by_name(self):
        """Test retrieving database by display name or filename"""
        registry = DatabaseRegistry()

        # Test by display name (case-insensitive)
        db = registry.get_database_by_name("sample")
        assert db is not None, "Should find database with 'sample' alias"

        # Test by filename
        db2 = registry.get_database_by_name("readathon_sample.db")
        assert db2 is not None, "Should find database by filename"

        # Test case insensitivity
        db3 = registry.get_database_by_name("SAMPLE")
        assert db3 is not None, "Should be case-insensitive"

        registry.close()
        print("✓ get_database_by_name works with multiple formats")

    def test_set_active_database(self):
        """Test activating a database"""
        registry = DatabaseRegistry()
        databases = registry.list_databases()

        if len(databases) >= 2:
            # Get two different database IDs
            db1_id = databases[0]['db_id']
            db2_id = databases[1]['db_id']

            # Activate first database
            result = registry.set_active_database(db1_id)
            assert result['success'] == True

            # Verify it's active
            db1 = registry.get_database(db1_id)
            assert db1['is_active'] == 1

            # Activate second database
            result = registry.set_active_database(db2_id)
            assert result['success'] == True

            # Verify first is now inactive, second is active
            db1_updated = registry.get_database(db1_id)
            db2_updated = registry.get_database(db2_id)

            assert db1_updated['is_active'] == 0, "Previous active database should be deactivated"
            assert db2_updated['is_active'] == 1, "New database should be active"

        registry.close()
        print("✓ set_active_database correctly manages active state")

    def test_recalculate_stats_from_file(self):
        """Test recalculating statistics from actual database file"""
        registry = DatabaseRegistry()

        # Find sample database
        db = registry.get_database_by_name("sample")

        if db:
            result = registry.recalculate_stats_from_file(db['db_id'])

            assert result['success'] == True
            assert 'student_count' in result
            assert 'total_days' in result
            assert 'total_donations' in result

            # Verify stats were updated in registry
            updated_db = registry.get_database(db['db_id'])
            assert updated_db['student_count'] == result['student_count']
            assert updated_db['total_days'] == result['total_days']
            assert updated_db['total_donations'] == result['total_donations']

        registry.close()
        print("✓ recalculate_stats_from_file updates registry correctly")

    def test_update_stats_manual(self):
        """Test manually updating statistics"""
        registry = DatabaseRegistry()
        databases = registry.list_databases()

        if databases:
            db_id = databases[0]['db_id']

            # Update stats manually
            result = registry.update_stats(
                db_id,
                student_count=999,
                total_days=99,
                total_donations=9999.99
            )

            assert result['success'] == True

            # Verify updated
            db = registry.get_database(db_id)
            assert db['student_count'] == 999
            assert db['total_days'] == 99
            assert db['total_donations'] == 9999.99

            # Restore original stats
            registry.recalculate_stats_from_file(db_id)

        registry.close()
        print("✓ update_stats manually updates values")


class TestRegistryAPIEndpoints:
    """Test Flask API endpoints for registry operations"""

    def test_api_list_databases(self, client):
        """Test GET /api/databases endpoint"""
        response = client.get('/api/databases')

        assert response.status_code == 200

        data = response.get_json()
        assert isinstance(data, list)

        if data:
            assert 'db_id' in data[0]
            assert 'display_name' in data[0]
            assert 'db_filename' in data[0]

        print("✓ GET /api/databases returns database list")

    def test_api_activate_database(self, client):
        """Test PUT /api/databases/<db_id>/activate endpoint"""
        # Get list of databases
        response = client.get('/api/databases')
        databases = response.get_json()

        if len(databases) >= 2:
            # Activate a database
            db_id = databases[0]['db_id']
            response = client.put(f'/api/databases/{db_id}/activate')

            assert response.status_code == 200

            data = response.get_json()
            assert data['success'] == True

        print("✓ PUT /api/databases/<db_id>/activate works")

    def test_api_update_stats(self, client):
        """Test PUT /api/databases/<db_id>/stats endpoint"""
        # Get list of databases
        response = client.get('/api/databases')
        databases = response.get_json()

        if databases:
            db_id = databases[0]['db_id']

            # Update stats
            response = client.put(f'/api/databases/{db_id}/stats')

            assert response.status_code == 200

            data = response.get_json()
            assert data['success'] == True
            assert 'student_count' in data
            assert 'total_days' in data
            assert 'total_donations' in data

        print("✓ PUT /api/databases/<db_id>/stats recalculates correctly")

    def test_api_set_active_database(self, client):
        """Test POST /api/set_active_database endpoint"""
        # Get list of databases
        response = client.get('/api/databases')
        databases = response.get_json()

        if databases:
            db_id = databases[0]['db_id']

            # Set active database
            response = client.post('/api/set_active_database',
                                   json={'database_id': db_id})

            assert response.status_code == 200

            data = response.get_json()
            assert data['success'] == True
            assert 'database' in data

        print("✓ POST /api/set_active_database works")


class TestRegistryIntegration:
    """Integration tests for registry system"""

    def test_database_switching_workflow(self, client):
        """Test complete workflow of switching between databases"""
        # Get list of databases
        response = client.get('/api/databases')
        databases = response.get_json()

        if len(databases) >= 2:
            # Switch to first database
            db1_id = databases[0]['db_id']
            response = client.post('/api/set_active_database',
                                   json={'database_id': db1_id})
            assert response.status_code == 200

            # Verify it's active
            response = client.get('/api/databases')
            databases = response.get_json()
            active_dbs = [db for db in databases if db['is_active']]
            assert len(active_dbs) == 1
            assert active_dbs[0]['db_id'] == db1_id

            # Switch to second database
            db2_id = databases[1]['db_id']
            response = client.post('/api/set_active_database',
                                   json={'database_id': db2_id})
            assert response.status_code == 200

            # Verify only second is active
            response = client.get('/api/databases')
            databases = response.get_json()
            active_dbs = [db for db in databases if db['is_active']]
            assert len(active_dbs) == 1
            assert active_dbs[0]['db_id'] == db2_id

        print("✓ Database switching workflow maintains correct active state")

    def test_stats_update_workflow(self, client):
        """Test workflow of updating database statistics"""
        # Get list of databases
        response = client.get('/api/databases')
        databases = response.get_json()

        if databases:
            db_id = databases[0]['db_id']
            original_stats = {
                'student_count': databases[0]['student_count'],
                'total_days': databases[0]['total_days'],
                'total_donations': databases[0]['total_donations']
            }

            # Update stats
            response = client.put(f'/api/databases/{db_id}/stats')
            assert response.status_code == 200

            result = response.get_json()
            assert result['success'] == True

            # Verify stats are updated in list
            response = client.get('/api/databases')
            databases = response.get_json()
            updated_db = next(db for db in databases if db['db_id'] == db_id)

            # Stats should match what was recalculated
            assert updated_db['student_count'] == result['student_count']
            assert updated_db['total_days'] == result['total_days']
            assert updated_db['total_donations'] == result['total_donations']

        print("✓ Stats update workflow correctly propagates changes")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("DATABASE REGISTRY TESTS")
    print("="*60 + "\n")

    pytest.main([__file__, '-v', '-s'])
