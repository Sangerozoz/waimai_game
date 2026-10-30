export type Point = [number, number];
export type Preference = 'fast' | 'main' | 'smooth';
export interface MapNode { id: string; x: number; y: number }
export interface MapRoad {
  id: string; nodes: string[]; kind: string; direction: number;
  width: number; speed: number; roughness: number; bridge: boolean;
}
export interface MapArea { points: Point[]; kind: string }
export interface MapLabel { text: string; x: number; y: number; kind: string; angle?: number }
export interface MapPOI { name: string; node: string; kind: string; address?:string }
export interface CityData {
  title: string; width: number; height: number;
  nodes: MapNode[]; roads: MapRoad[]; buildings: Point[][];
  areas: MapArea[]; waterways: Point[][]; labels: MapLabel[]; pois: MapPOI[];
  playBounds?:import('./CityExtent').Bounds;
  dispatchBounds?:import('./CityExtent').Bounds;
  dispatchAreas?:Record<string,import('./DispatchAreas').PlaceArea>;
  urbanBounds?:import('./CityExtent').Bounds;
  operatingPOIs?:number[];
  legacyMapIds?:string[];
  placeCatalogVersion?:1|2|3|4;
}
export interface RouteSegment { from: string; to: string; road: string; metres: number; seconds: number; roughness: number }
export interface MapRoute {
  preference: Preference; nodes: string[]; points: Point[]; segments: RouteSegment[];
  metres: number; seconds: number; risk: number;
  pickupIndex?: number;
}
