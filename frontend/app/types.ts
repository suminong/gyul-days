export type Author = {
  id: number;
  username: string;
};


export type Entry = {
  id: number;
  content: string;
  created_at: string;
  author: Author;
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