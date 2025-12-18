import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search, Calendar } from "lucide-react";

export const SearchBar = ({ onSearch }) => {
  const [searchParams, setSearchParams] = useState({
    departure: "",
    arrival: "",
    departure_date: "",
    return_date: "",
    passengers: 1,
    min_discount: 50,
    offer_type: "all"
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(searchParams);
  };

  return (
    <div className="bg-white rounded-xl shadow-xl p-6 border border-slate-200" data-testid="search-bar">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Offer Type */}
          <div data-testid="offer-type-selector">
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Type
            </label>
            <Select
              value={searchParams.offer_type}
              onValueChange={(value) => setSearchParams({ ...searchParams, offer_type: value })}
            >
              <SelectTrigger data-testid="offer-type-trigger">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Deals</SelectItem>
                <SelectItem value="flight">Flights Only</SelectItem>
                <SelectItem value="cruise">Cruises Only</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Departure */}
          <div data-testid="departure-input-group">
            <label className="block text-sm font-medium text-slate-700 mb-2">
              From (Airport Code)
            </label>
            <Input
              type="text"
              placeholder="e.g., JFK"
              value={searchParams.departure}
              onChange={(e) => setSearchParams({ ...searchParams, departure: e.target.value.toUpperCase() })}
              maxLength={3}
              data-testid="departure-input"
              className="font-mono"
            />
          </div>

          {/* Arrival */}
          <div data-testid="arrival-input-group">
            <label className="block text-sm font-medium text-slate-700 mb-2">
              To (Airport Code)
            </label>
            <Input
              type="text"
              placeholder="e.g., LAX"
              value={searchParams.arrival}
              onChange={(e) => setSearchParams({ ...searchParams, arrival: e.target.value.toUpperCase() })}
              maxLength={3}
              data-testid="arrival-input"
              className="font-mono"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Departure Date */}
          <div data-testid="departure-date-group">
            <label className="block text-sm font-medium text-slate-700 mb-2">
              <Calendar className="inline w-4 h-4 mr-1" />
              Departure Date
            </label>
            <Input
              type="date"
              value={searchParams.departure_date}
              onChange={(e) => setSearchParams({ ...searchParams, departure_date: e.target.value })}
              data-testid="departure-date-input"
            />
          </div>

          {/* Return Date */}
          <div data-testid="return-date-group">
            <label className="block text-sm font-medium text-slate-700 mb-2">
              <Calendar className="inline w-4 h-4 mr-1" />
              Return Date (Optional)
            </label>
            <Input
              type="date"
              value={searchParams.return_date}
              onChange={(e) => setSearchParams({ ...searchParams, return_date: e.target.value })}
              data-testid="return-date-input"
            />
          </div>

          {/* Min Discount */}
          <div data-testid="min-discount-group">
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Min Discount: {searchParams.min_discount}%
            </label>
            <input
              type="range"
              min="50"
              max="90"
              step="5"
              value={searchParams.min_discount}
              onChange={(e) => setSearchParams({ ...searchParams, min_discount: parseInt(e.target.value) })}
              data-testid="min-discount-slider"
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>
        </div>

        <Button
          type="submit"
          className="w-full bg-blue-600 hover:bg-blue-700 text-white h-12 rounded-full font-semibold shadow-lg shadow-blue-600/20 hover:scale-105 active:scale-95 transition-all"
          data-testid="search-button"
        >
          <Search className="mr-2 h-5 w-5" />
          Search Deals
        </Button>
      </form>
    </div>
  );
};

export default SearchBar;