export type Author = {
  id: number;
  username: string;
};

export type EntryImage = {
  id: number;
  entry_id: number;

  storage_provider:
    string | null;

  storage_key:
    string | null;

  display_url:
    string | null;

  original_filename:
    string | null;

  content_type:
    string | null;

  created_at: string;
};


export type Entry = {
  id: number;
  content: string;
  created_at: string;
  author: Author;
  images: EntryImage[];
  tag_links: EntryTag[];
  analysis: EntryAnalysis | null;
};


export type User = {
  id: number;
  username: string;
  email: string;
  created_at: string;
};


export type Space = {
  id: number;
  name: string;
  created_at: string;
};

export type Tag = {
  id: number;
  name: string;
  created_at: string;
};


export type EntryTag = {
  id: number;
  source: string;
  confidence: number | null;
  tag: Tag;
};

export type StreakResponse = {
  current_streak: number;
  longest_streak: number;
  total_recorded_days: number;
  stage:
    | "none"
    | "orange"
    | "two_oranges"
    | "box"
    | "tree";
  next_milestone: number | null;
};

export type EntryAnalysis = {
  id: number;
  entry_id: number;
  emotional_intensity: number;
  length_score: number;
  gyul_intensity: number;
  mood_label: string;
  detected_language: string | null;
  analysis_source: string;
  created_at: string;
};