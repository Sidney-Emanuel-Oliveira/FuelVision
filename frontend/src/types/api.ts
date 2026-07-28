export interface PriceFilters {
  product: string;
  state: string;
  municipality: string;
  startDate: string;
  endDate: string;
}

export interface PriceSummary {
  product: string;
  unit: string;
  observationCount: number;
  averageSalePrice: number;
  minimumSalePrice: number;
  maximumSalePrice: number;
  priceRange: number;
  firstCollectionDate: string;
  lastCollectionDate: string;
}

export interface PriceHistoryPoint {
  collectionDate: string;
  product: string;
  unit: string;
  observationCount: number;
  averageSalePrice: number;
  minimumSalePrice: number;
  maximumSalePrice: number;
  priceRange: number;
}

export interface PageResponse<T> {
  items: T[];
  totalItems: number;
  totalPages: number;
  page: number;
  size: number;
}

export interface StateLocation {
  code: string;
  name: string;
}

export interface CityLocation {
  id: number;
  name: string;
  stateCode: string;
}

export interface LocationComparisonPoint {
  stateCode: string;
  stateName: string;
  averageSalePrice: number;
  observationCount: number;
}
