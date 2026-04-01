// --- Request ---

export interface ClassifyRequest {
  image: Blob;
  detectedClass: string;
  confidence: number;
  regionCode?: string;
}

// --- Response ---

export interface ClassifyDetailResponse {
  detectedClass: string;
  confirmedClass: string;
  confidence: number;
  disposalMethod: DisposalMethodResponse;
  costInfo: CostInfoResponse;
  warnings: string[];
  regionSpecific: string;
  source: "PUBLIC_API" | "VECTOR_CACHE" | "VLM_REALTIME";
  cached: boolean;
}

export interface DisposalMethodResponse {
  method: string;
  notes: string[];
  items: DisposalItemResponse[];
}

export interface DisposalItemResponse {
  label: string;
  action: string;
}

export interface CostInfoResponse {
  type: string;
  amount: number;
  currency: string;
  collectionSchedule: string;
  notes: string;
}

// --- YOLO (온디바이스) ---

export interface YOLOResult {
  className: string;
  confidence: number;
  boundingBox?: [number, number, number, number];
}
