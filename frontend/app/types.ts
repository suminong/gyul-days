export type Author = {
  id: number;
  username: string;
};


export type EntryImage = {
  id: number;
  entry_id: number;
  file_path: string;
  original_filename: string | null;
  content_type: string | null;
  created_at: string;
};


export type Entry = {
  id: number;
  content: string;
  created_at: string;
  author: Author;
  images: EntryImage[];
  tag_links: EntryTag[];
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