import requests
import sys
import json
import time
from datetime import datetime

class VoloWebScrapingTester:
    def __init__(self, base_url="https://travel-promo-radar-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.failed_tests = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test_name": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    Details: {details}")

    def test_health_endpoint(self):
        """Test /api/health endpoint"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Status: {data.get('status')}, Timestamp: {data.get('timestamp')}"
            else:
                details = f"Status code: {response.status_code}"
            
            self.log_test("Health Check", success, details)
            return success
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {str(e)}")
            return False

    def test_stats_endpoint(self):
        """Test /api/stats endpoint"""
        try:
            response = requests.get(f"{self.api_url}/stats", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ['total_offers', 'flight_offers', 'cruise_offers', 
                                 'flight_avg_discount', 'cruise_avg_discount']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details = f"Missing fields: {missing_fields}"
                else:
                    details = f"Total offers: {data['total_offers']}, Flights: {data['flight_offers']}, Cruises: {data['cruise_offers']}"
            else:
                details = f"Status code: {response.status_code}"
            
            self.log_test("Stats Endpoint", success, details)
            return success, data if success else {}
        except Exception as e:
            self.log_test("Stats Endpoint", False, f"Error: {str(e)}")
            return False, {}

    def test_offers_endpoint(self):
        """Test /api/offers endpoint"""
        try:
            # Test default offers
            response = requests.get(f"{self.api_url}/offers", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                offers = data.get('offers', [])
                details = f"Retrieved {len(offers)} offers"
                
                # Validate offer structure
                if offers:
                    first_offer = offers[0]
                    required_fields = ['id', 'type', 'original_price', 'current_price', 'discount_percentage']
                    missing_fields = [field for field in required_fields if field not in first_offer]
                    
                    if missing_fields:
                        success = False
                        details += f", Missing fields in offers: {missing_fields}"
            else:
                details = f"Status code: {response.status_code}"
            
            self.log_test("Offers Endpoint (Default)", success, details)
            
            # Test with filters
            params = {"offer_type": "flight", "min_discount": 60, "limit": 10}
            response = requests.get(f"{self.api_url}/offers", params=params, timeout=10)
            filter_success = response.status_code == 200
            
            if filter_success:
                data = response.json()
                offers = data.get('offers', [])
                details = f"Filtered offers: {len(offers)} flight offers with 60%+ discount"
            else:
                details = f"Filter test failed with status: {response.status_code}"
            
            self.log_test("Offers Endpoint (Filtered)", filter_success, details)
            return success and filter_success
        except Exception as e:
            self.log_test("Offers Endpoint", False, f"Error: {str(e)}")
            return False

    def test_search_endpoint(self):
        """Test /api/search endpoint"""
        try:
            # Test basic search
            search_data = {
                "departure": "JFK",
                "arrival": "LAX",
                "departure_date": "2024-12-01",
                "passengers": 1,
                "min_discount": 50,
                "offer_type": "all"
            }
            
            response = requests.post(f"{self.api_url}/search", 
                                   json=search_data, 
                                   headers={'Content-Type': 'application/json'},
                                   timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                offers = data.get('offers', [])
                search_id = data.get('search_id')
                details = f"Search returned {len(offers)} offers, Search ID: {search_id[:8] if search_id else 'None'}"
                
                # Validate search response structure
                required_fields = ['search_id', 'total_results', 'offers', 'timestamp']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details += f", Missing response fields: {missing_fields}"
            else:
                details = f"Status code: {response.status_code}"
            
            self.log_test("Search Endpoint", success, details)
            return success
        except Exception as e:
            self.log_test("Search Endpoint", False, f"Error: {str(e)}")
            return False

    def test_offer_validation(self):
        """Test offer authenticity validation"""
        try:
            # Get some offers first
            response = requests.get(f"{self.api_url}/offers?limit=5", timeout=10)
            if response.status_code != 200:
                self.log_test("Offer Validation", False, "Could not fetch offers for validation test")
                return False
            
            data = response.json()
            offers = data.get('offers', [])
            
            if not offers:
                self.log_test("Offer Validation", False, "No offers available for validation test")
                return False
            
            # Check if offers have validation fields
            validated_offers = [offer for offer in offers if offer.get('is_authentic') is not None]
            validation_timestamps = [offer for offer in offers if 'validation_timestamp' in offer]
            
            success = len(validated_offers) > 0 and len(validation_timestamps) > 0
            details = f"Validated offers: {len(validated_offers)}/{len(offers)}, With timestamps: {len(validation_timestamps)}/{len(offers)}"
            
            self.log_test("Offer Validation", success, details)
            return success
        except Exception as e:
            self.log_test("Offer Validation", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Volo Backend API Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 50)
        
        # Test basic connectivity
        health_ok = self.test_health_endpoint()
        if not health_ok:
            print("\n❌ CRITICAL: Health check failed - backend may be down")
            return self.get_results()
        
        # Test all endpoints
        self.test_stats_endpoint()
        self.test_offers_endpoint()
        self.test_search_endpoint()
        self.test_offer_validation()
        
        return self.get_results()

    def get_results(self):
        """Get test results summary"""
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed ({success_rate:.1f}%)")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed - check details above")
        
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "success_rate": success_rate,
            "test_details": self.test_results
        }

def main():
    tester = VoloAPITester()
    results = tester.run_all_tests()
    
    # Return appropriate exit code
    return 0 if results["success_rate"] == 100 else 1

if __name__ == "__main__":
    sys.exit(main())