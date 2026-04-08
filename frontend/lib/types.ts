export type ExtractedText = {
  headline: string;
  subheadline: string;
  cta: string;
  offer: string;
  brand_name: string;
};

export type VisualDescription = {
  product_type: string;
  layout: string;
  colors: string[];
  style: string;
  background: string;
  extras: string[];
};

export type AdAnalysis = {
  image_id: string;
  image_path: string;
  extracted_text: ExtractedText;
  visual_description: VisualDescription;
};

export type PatternReport = {
  summary: string;
  common_layouts: string[];
  recurring_palettes: string[];
  style_patterns: string[];
  copy_tone: string;
  cta_patterns: string[];
};

export type TemplateResult = {
  template: string;
  variables: string[];
};

export type FinalPromptRequest = {
  product_name: string;
  product_benefit: string;
  cta_text: string;
  target_audience: string;
};
