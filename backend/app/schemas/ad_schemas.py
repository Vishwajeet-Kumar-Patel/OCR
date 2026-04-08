from pydantic import BaseModel, Field


class ExtractedText(BaseModel):
    headline: str = ""
    subheadline: str = ""
    cta: str = ""
    offer: str = ""
    brand_name: str = ""


class VisualDescription(BaseModel):
    product_type: str = ""
    layout: str = ""
    colors: list[str] = Field(default_factory=list)
    style: str = ""
    background: str = ""
    extras: list[str] = Field(default_factory=list)


class AdAnalysis(BaseModel):
    image_id: str
    image_path: str
    extracted_text: ExtractedText
    visual_description: VisualDescription


class AnalyzeAdsRequest(BaseModel):
    job_id: str


class AnalyzeAdsResponse(BaseModel):
    analyses: list[AdAnalysis]


class PatternReport(BaseModel):
    summary: str
    common_layouts: list[str]
    recurring_palettes: list[str]
    style_patterns: list[str]
    copy_tone: str
    cta_patterns: list[str]


class PromptTemplateResponse(BaseModel):
    template: str
    variables: list[str]


class PromptInputs(BaseModel):
    product_name: str
    product_benefit: str
    cta_text: str
    target_audience: str


class GeneratePromptRequest(BaseModel):
    job_id: str
    inputs: PromptInputs


class GeneratePromptResponse(BaseModel):
    prompt: str
