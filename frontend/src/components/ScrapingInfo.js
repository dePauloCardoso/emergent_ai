import { useState, useEffect } from "react";
import axios from "axios";
import { Globe, Plane, Ship } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const ScrapingInfo = () => {
  const [scrapingInfo, setScrapingInfo] = useState(null);

  useEffect(() => {
    const fetchScrapingInfo = async () => {
      try {
        const response = await axios.get(`${API}/scraping-info`);
        setScrapingInfo(response.data);
      } catch (error) {
        console.error("Error fetching scraping info:", error);
      }
    };

    fetchScrapingInfo();
  }, []);

  if (!scrapingInfo) return null;

  return (
    <div className="bg-gradient-to-r from-blue-50 to-slate-50 rounded-xl p-6 border border-blue-100" data-testid="scraping-info">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-blue-600 rounded-lg">
          <Globe className="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 className="font-bold text-slate-900 font-heading">Fontes de Dados: Web Scraping Direto</h3>
          <p className="text-sm text-slate-600">Atualizado automaticamente a cada hora</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
        {/* Flight Sources */}
        <div className="bg-white rounded-lg p-4 border border-slate-200">
          <div className="flex items-center gap-2 mb-3">
            <Plane className="w-5 h-5 text-blue-600" />
            <h4 className="font-semibold text-slate-900">Companhias Aéreas</h4>
            <span className="ml-auto text-sm font-bold text-blue-600">{scrapingInfo.flight_sources.total}</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {scrapingInfo.flight_sources.airlines.slice(0, 6).map((airline, index) => (
              <span 
                key={index} 
                className="text-xs px-2 py-1 bg-blue-50 text-blue-700 rounded-full border border-blue-200"
              >
                {airline}
              </span>
            ))}
            {scrapingInfo.flight_sources.airlines.length > 6 && (
              <span className="text-xs px-2 py-1 bg-slate-100 text-slate-600 rounded-full">
                +{scrapingInfo.flight_sources.airlines.length - 6} mais
              </span>
            )}
          </div>
        </div>

        {/* Cruise Sources */}
        <div className="bg-white rounded-lg p-4 border border-slate-200">
          <div className="flex items-center gap-2 mb-3">
            <Ship className="w-5 h-5 text-blue-600" />
            <h4 className="font-semibold text-slate-900">Linhas de Cruzeiro</h4>
            <span className="ml-auto text-sm font-bold text-blue-600">{scrapingInfo.cruise_sources.total}</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {scrapingInfo.cruise_sources.cruise_lines.slice(0, 6).map((line, index) => (
              <span 
                key={index} 
                className="text-xs px-2 py-1 bg-blue-50 text-blue-700 rounded-full border border-blue-200"
              >
                {line}
              </span>
            ))}
            {scrapingInfo.cruise_sources.cruise_lines.length > 6 && (
              <span className="text-xs px-2 py-1 bg-slate-100 text-slate-600 rounded-full">
                +{scrapingInfo.cruise_sources.cruise_lines.length - 6} mais
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="mt-4 p-3 bg-emerald-50 border border-emerald-200 rounded-lg">
        <p className="text-xs text-emerald-900">
          ✓ Todos os dados são extraídos diretamente dos sites oficiais usando web scraping automatizado
        </p>
      </div>
    </div>
  );
};

export default ScrapingInfo;
