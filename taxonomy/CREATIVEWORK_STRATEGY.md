# CreativeWork Ontology Strategy

Agent Book should support the full schema.org `CreativeWork` subtree as its base content ontology.

The platform should not only support a few manually selected document types. It should ingest or model the complete CreativeWork family and then extend it with enterprise artifact patterns, workflows, evidence, validation, governance, and exports.

## Product Principle

```text
schema.org CreativeWork subtree
  -> Agent Book CreativeWork Base Ontology
  -> Enterprise Artifact Pattern
  -> Artifact Run
  -> Generated Output / Export
```

Schema.org CreativeWork answers: **what kind of work is this?**

Agent Book answers: **how do we create, govern, validate, and export it for enterprise use?**

## Scope

Focus only on `CreativeWork` and its descendants.

Examples include:

- Article
- BlogPosting
- Report
- ScholarlyArticle
- Book
- Chapter
- Claim
- Comment
- Conversation
- Course
- CreativeWorkSeason
- CreativeWorkSeries
- DataCatalog
- Dataset
- DigitalDocument
- NoteDigitalDocument
- PresentationDigitalDocument
- SpreadsheetDigitalDocument
- TextDigitalDocument
- Drawing
- Episode
- ExercisePlan
- FAQPage
- HowTo
- ImageObject
- LearningResource
- Legislation
- Manuscript
- Map
- MathSolver
- MediaObject
- AudioObject
- VideoObject
- MusicComposition
- MusicPlaylist
- MusicRecording
- Painting
- Photograph
- Play
- PodcastEpisode
- PodcastSeason
- PodcastSeries
- Poster
- PublicationIssue
- PublicationVolume
- Question
- Quiz
- Review
- Sculpture
- SheetMusic
- ShortStory
- SoftwareApplication
- SoftwareSourceCode
- SpecialAnnouncement
- Statement
- TVSeason
- TVSeries
- Thesis
- VisualArtwork
- WebContent
- WebPage

This list is not intended to be final. The implementation should support the full CreativeWork subtree from schema.org, preferably through ingestion or generated taxonomy data.

## Do Not Treat CreativeWork As Enough

CreativeWork is only the base type system.

Agent Book still needs deeper enterprise layers:

```text
CreativeWork Type
  + Enterprise Purpose
  + Artifact Pattern
  + Workflow
  + Evidence Model
  + Template Model
  + Governance Model
  + Export Targets
```

## Internal Type Model

Each supported CreativeWork subtype should become a normalized internal object:

```yaml
id: schema:Report
label: Report
base_type: schema:CreativeWork
parent_types:
  - schema:CreativeWork
child_types: []
properties:
  - name
  - description
  - author
  - creator
  - dateCreated
  - dateModified
  - publisher
  - about
  - audience
  - citation
source: schema.org
```

## Enterprise Extension Model

Agent Book should extend CreativeWork types with enterprise generation metadata:

```yaml
agentbook:
  artifact_family:
  artifact_pattern:
  business_process:
  workflow:
  evidence_requirements:
  governance_rules:
  validation_rules:
  export_targets:
  lifecycle_state:
  approval_state:
```

## Mapping Examples

### State of Cybersecurity Report

```yaml
schema_type: schema:Report
creativework_family: StrategicInsightReport
artifact_pattern: state_of_report
business_process: market_intelligence
outputs:
  - pdf_report
  - pptx_deck
  - executive_memo
```

### Product Comparison Article

```yaml
schema_type: schema:Article
creativework_family: ContentMarketingAsset
artifact_pattern: product_comparison_article
business_process: demand_generation
outputs:
  - markdown_article
  - html_article
  - comparison_table
```

### Product Walkthrough Video

```yaml
schema_type: schema:VideoObject
creativework_family: ProductEducationAsset
artifact_pattern: product_walkthrough_video
business_process: customer_education
outputs:
  - video_script
  - storyboard
  - narration_script
```

### Readiness Assessment

```yaml
schema_type: schema:DigitalDocument
creativework_family: AssessmentArtifact
artifact_pattern: readiness_assessment
business_process: advisory_or_evaluation
outputs:
  - assessment_report_pdf
  - scorecard
  - roadmap
```

## Implementation Plan

1. Add a CreativeWork ontology ingestion/generation script.
2. Store normalized CreativeWork types in `taxonomy/creativework/types/`.
3. Allow each ArtifactPattern to declare one or more compatible CreativeWork schema types.
4. Validate artifact outputs against both:
   - base CreativeWork type expectations
   - Agent Book enterprise workflow requirements
5. Use CreativeWork mapping for interoperability, metadata, search, and export packaging.

## MVP Requirement

The first implementation should support these CreativeWork types at minimum:

- Report
- Article
- BlogPosting
- DigitalDocument
- PresentationDigitalDocument
- VideoObject
- HowTo
- Course
- LearningResource
- Review
- Dataset
- FAQPage
- WebPage

The architecture, however, should be designed to support the entire CreativeWork subtree over time.
