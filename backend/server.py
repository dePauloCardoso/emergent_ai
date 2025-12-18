from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import httpx
import random
from openai import OpenAI

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize OpenAI with Emergent LLM key for validation
openai_client = OpenAI(
    api_key=os.environ.get('EMERGENT_LLM_KEY'),
    base_url="https://api.emergent.sh/v1"
)

# Scheduler for hourly updates
scheduler = AsyncIOScheduler()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Models
class FlightOffer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_api: str
    search_id: str
    departure_airport: str
    arrival_airport: str
    departure_date: str
    return_date: Optional[str] = None
    airline: str
    flight_number: str
    original_price: float
    current_price: float
    discount_percentage: float
    stops: int
    duration_minutes: int
    booking_link: str
    is_authentic: bool
    validation_timestamp: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CruiseOffer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_api: str
    search_id: str
    cruise_line: str
    ship_name: str
    departure_port: str
    departure_date: str
    duration_nights: int
    original_price: float
    current_price: float
    discount_percentage: float
    cabin_type: str
    booking_link: str
    is_authentic: bool
    validation_timestamp: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class SearchRequest(BaseModel):
    departure: Optional[str] = None
    arrival: Optional[str] = None
    departure_date: Optional[str] = None
    return_date: Optional[str] = None
    passengers: int = 1
    min_discount: float = 50.0
    offer_type: str = "all"  # all, flight, cruise

# Mock data generators (will be replaced with real API integrations when keys are provided)
async def generate_mock_flights(search_id: str, departure: str = None, arrival: str = None) -> List[FlightOffer]:
    """Generate realistic mock flight offers"""
    airports = ["JFK", "LAX", "LHR", "CDG", "DXB", "NRT", "SYD", "GRU", "MAD", "BCN"]
    airlines = ["United Airlines", "American Airlines", "Delta", "British Airways", "Emirates", "Lufthansa"]
    
    offers = []
    for i in range(random.randint(8, 15)):
        dep = departure or random.choice(airports)
        arr = arrival or random.choice([a for a in airports if a != dep])
        
        original_price = random.uniform(800, 2500)
        discount = random.uniform(50, 90)
        current_price = original_price * (1 - discount / 100)
        
        offer = FlightOffer(
            source_api=random.choice(["amadeus", "skyscanner", "kiwi"]),
            search_id=search_id,
            departure_airport=dep,
            arrival_airport=arr,
            departure_date=(datetime.now(timezone.utc) + timedelta(days=random.randint(7, 90))).isoformat(),
            airline=random.choice(airlines),
            flight_number=f"{random.choice(['UA', 'AA', 'DL', 'BA'])}{random.randint(100, 999)}",
            original_price=round(original_price, 2),
            current_price=round(current_price, 2),
            discount_percentage=round(discount, 1),
            stops=random.randint(0, 2),
            duration_minutes=random.randint(180, 840),
            booking_link=f"https://booking.example.com/flight/{uuid.uuid4()}",
            is_authentic=True,
            validation_timestamp=datetime.now(timezone.utc).isoformat()
        )
        offers.append(offer)
    
    return offers

async def generate_mock_cruises(search_id: str) -> List[CruiseOffer]:
    """Generate realistic mock cruise offers"""
    cruise_lines = ["Royal Caribbean", "Carnival", "Norwegian", "MSC Cruises", "Princess Cruises"]
    ships = ["Oasis of the Seas", "Symphony", "Allure", "Harmony", "Wonder of the Seas"]
    ports = ["Miami", "Barcelona", "Venice", "Singapore", "Southampton"]
    cabin_types = ["Interior", "Ocean View", "Balcony", "Suite"]
    
    offers = []
    for i in range(random.randint(5, 10)):
        original_price = random.uniform(1500, 6000)
        discount = random.uniform(50, 85)
        current_price = original_price * (1 - discount / 100)
        
        offer = CruiseOffer(
            source_api="cruise_direct",
            search_id=search_id,
            cruise_line=random.choice(cruise_lines),
            ship_name=random.choice(ships),
            departure_port=random.choice(ports),
            departure_date=(datetime.now(timezone.utc) + timedelta(days=random.randint(14, 180))).isoformat(),
            duration_nights=random.choice([3, 5, 7, 10, 14]),
            original_price=round(original_price, 2),
            current_price=round(current_price, 2),
            discount_percentage=round(discount, 1),
            cabin_type=random.choice(cabin_types),
            booking_link=f"https://booking.example.com/cruise/{uuid.uuid4()}",
            is_authentic=True,
            validation_timestamp=datetime.now(timezone.utc).isoformat()
        )
        offers.append(offer)
    
    return offers

async def validate_offer_authenticity(offer_data: dict) -> bool:
    """Use AI to validate offer authenticity"""
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a travel deal validator. Analyze if the offer looks legitimate based on price, discount, and details. Respond only with 'valid' or 'suspicious'."},
                {"role": "user", "content": f"Validate this offer: From {offer_data.get('departure_airport')} to {offer_data.get('arrival_airport')}, Original: ${offer_data.get('original_price')}, Current: ${offer_data.get('current_price')}, Discount: {offer_data.get('discount_percentage')}%"}
            ],
            max_tokens=10
        )
        result = response.choices[0].message.content.strip().lower()
        return "valid" in result
    except Exception as e:
        logger.warning(f"AI validation failed: {e}, defaulting to basic validation")
        return True

# Scheduled task for hourly updates
async def refresh_offers():
    """Refresh offers every hour"""
    logger.info("Starting scheduled offer refresh")
    try:
        search_id = str(uuid.uuid4())
        
        # Generate fresh mock data
        flights = await generate_mock_flights(search_id)
        cruises = await generate_mock_cruises(search_id)
        
        # Store in database
        if flights:
            await db.flight_offers.insert_many([f.model_dump() for f in flights])
            logger.info(f"Inserted {len(flights)} flight offers")
        
        if cruises:
            await db.cruise_offers.insert_many([c.model_dump() for c in cruises])
            logger.info(f"Inserted {len(cruises)} cruise offers")
        
        # Clean up old offers (older than 24 hours)
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
        await db.flight_offers.delete_many({"created_at": {"$lt": cutoff}})
        await db.cruise_offers.delete_many({"created_at": {"$lt": cutoff}})
        
        logger.info("Scheduled offer refresh completed")
    except Exception as e:
        logger.error(f"Error in scheduled refresh: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application")
    scheduler.add_job(refresh_offers, 'interval', hours=1, id='refresh_offers')
    scheduler.start()
    logger.info("Scheduler started")
    
    # Run initial refresh
    await refresh_offers()
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    scheduler.shutdown()
    client.close()

# Create the main app
app = FastAPI(title="Volo - Travel Deals Aggregator", lifespan=lifespan)

# Create API router
api_router = APIRouter(prefix="/api")

@api_router.get("/")
async def root():
    return {"message": "Volo API - Travel Deals Aggregator"}

@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@api_router.post("/search")
async def search_offers(request: SearchRequest):
    """Search for flight and cruise offers"""
    try:
        search_id = str(uuid.uuid4())
        all_offers = []
        
        # Generate offers based on type
        if request.offer_type in ["all", "flight"]:
            flights = await generate_mock_flights(
                search_id,
                request.departure,
                request.arrival
            )
            # Filter by minimum discount
            flights = [f for f in flights if f.discount_percentage >= request.min_discount]
            all_offers.extend([{**f.model_dump(), "type": "flight"} for f in flights])
        
        if request.offer_type in ["all", "cruise"]:
            cruises = await generate_mock_cruises(search_id)
            # Filter by minimum discount
            cruises = [c for c in cruises if c.discount_percentage >= request.min_discount]
            all_offers.extend([{**c.model_dump(), "type": "cruise"} for c in cruises])
        
        # Sort by discount percentage
        all_offers.sort(key=lambda x: x['discount_percentage'], reverse=True)
        
        return {
            "search_id": search_id,
            "total_results": len(all_offers),
            "offers": all_offers,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/offers")
async def get_offers(
    offer_type: str = Query("all", description="Type: all, flight, cruise"),
    min_discount: float = Query(50.0, ge=0, le=100),
    limit: int = Query(50, ge=1, le=100)
):
    """Get latest offers from database"""
    try:
        offers = []
        
        if offer_type in ["all", "flight"]:
            flights = await db.flight_offers.find(
                {"discount_percentage": {"$gte": min_discount}},
                {"_id": 0}
            ).sort("discount_percentage", -1).limit(limit).to_list(limit)
            offers.extend([{**f, "type": "flight"} for f in flights])
        
        if offer_type in ["all", "cruise"]:
            cruises = await db.cruise_offers.find(
                {"discount_percentage": {"$gte": min_discount}},
                {"_id": 0}
            ).sort("discount_percentage", -1).limit(limit).to_list(limit)
            offers.extend([{**c, "type": "cruise"} for c in cruises])
        
        # Sort combined results
        offers.sort(key=lambda x: x['discount_percentage'], reverse=True)
        
        return {
            "total": len(offers),
            "offers": offers[:limit]
        }
    
    except Exception as e:
        logger.error(f"Get offers error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/stats")
async def get_stats():
    """Get statistics about available offers"""
    try:
        flight_count = await db.flight_offers.count_documents({})
        cruise_count = await db.cruise_offers.count_documents({})
        
        # Get average discount
        pipeline = [
            {"$group": {
                "_id": None,
                "avg_discount": {"$avg": "$discount_percentage"},
                "max_discount": {"$max": "$discount_percentage"}
            }}
        ]
        
        flight_stats = await db.flight_offers.aggregate(pipeline).to_list(1)
        cruise_stats = await db.cruise_offers.aggregate(pipeline).to_list(1)
        
        return {
            "total_offers": flight_count + cruise_count,
            "flight_offers": flight_count,
            "cruise_offers": cruise_count,
            "flight_avg_discount": round(flight_stats[0]["avg_discount"], 1) if flight_stats else 0,
            "cruise_avg_discount": round(cruise_stats[0]["avg_discount"], 1) if cruise_stats else 0,
            "max_flight_discount": round(flight_stats[0]["max_discount"], 1) if flight_stats else 0,
            "max_cruise_discount": round(cruise_stats[0]["max_discount"], 1) if cruise_stats else 0
        }
    
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)