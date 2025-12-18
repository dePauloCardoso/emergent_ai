import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Sliders } from "lucide-react";

export const FilterSidebar = ({ filters, onFilterChange }) => {
  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 sticky top-6" data-testid="filter-sidebar">
      <div className="flex items-center gap-2 mb-6">
        <Sliders className="w-5 h-5 text-slate-600" />
        <h3 className="font-semibold text-slate-900">Filters</h3>
      </div>

      <div className="space-y-6">
        {/* Offer Type */}
        <div data-testid="offer-type-filter">
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Deal Type
          </label>
          <Select
            value={filters.offerType}
            onValueChange={(value) => onFilterChange({ ...filters, offerType: value })}
          >
            <SelectTrigger data-testid="offer-type-select">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Deals</SelectItem>
              <SelectItem value="flight">Flights</SelectItem>
              <SelectItem value="cruise">Cruises</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Min Discount */}
        <div data-testid="min-discount-filter">
          <label className="block text-sm font-medium text-slate-700 mb-3">
            Minimum Discount: <span className="text-orange-600 font-bold">{filters.minDiscount}%</span>
          </label>
          <input
            type="range"
            min="50"
            max="90"
            step="5"
            value={filters.minDiscount}
            onChange={(e) => onFilterChange({ ...filters, minDiscount: parseInt(e.target.value) })}
            data-testid="min-discount-range"
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-orange-500"
          />
          <div className="flex justify-between text-xs text-slate-500 mt-1">
            <span>50%</span>
            <span>90%</span>
          </div>
        </div>

        {/* Sort By */}
        <div data-testid="sort-by-filter">
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Sort By
          </label>
          <Select
            value={filters.sortBy}
            onValueChange={(value) => onFilterChange({ ...filters, sortBy: value })}
          >
            <SelectTrigger data-testid="sort-by-select">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="discount">Highest Discount</SelectItem>
              <SelectItem value="price">Lowest Price</SelectItem>
              <SelectItem value="date">Soonest Departure</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Info Box */}
        <div className="p-4 bg-blue-50 rounded-lg border border-blue-100" data-testid="info-box">
          <p className="text-xs text-blue-900 leading-relaxed">
            All deals are verified in real-time and updated hourly from trusted sources.
          </p>
        </div>
      </div>
    </div>
  );
};

export default FilterSidebar;