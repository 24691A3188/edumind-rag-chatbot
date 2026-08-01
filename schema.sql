-- ========================================================
-- EduMind AI RAG Chatbot - Supabase PostgreSQL Schema DDL
-- ========================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- --------------------------------------------------------
-- 1. USERS TABLE (Syncs with auth.users)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.users (
  id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  role TEXT CHECK (role IN ('admin', 'student', 'customer', 'employee')) DEFAULT 'student',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- --------------------------------------------------------
-- 2. DOCUMENTS TABLE
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.documents (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  title TEXT NOT NULL,
  file_name TEXT NOT NULL,
  file_type TEXT NOT NULL,
  file_size INTEGER,
  chunk_count INTEGER DEFAULT 0,
  uploaded_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
  uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;

-- --------------------------------------------------------
-- 3. CHAT HISTORY TABLE
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.chat_history (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  retrieved_sources JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

ALTER TABLE public.chat_history ENABLE ROW LEVEL SECURITY;

-- --------------------------------------------------------
-- 4. FAQ TABLE
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.faqs (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  category TEXT DEFAULT 'General',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

ALTER TABLE public.faqs ENABLE ROW LEVEL SECURITY;

-- --------------------------------------------------------
-- 5. AUTOMATED USER REGISTRATION TRIGGER
-- --------------------------------------------------------
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, name, email, role)
  VALUES (
    new.id,
    COALESCE(new.raw_user_meta_data->>'name', 'New User'),
    new.email,
    COALESCE(new.raw_user_meta_data->>'role', 'student')
  )
  ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    email = EXCLUDED.email;
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- --------------------------------------------------------
-- 6. ROW LEVEL SECURITY (RLS) POLICIES
-- --------------------------------------------------------

-- Helper Security Definer Function (Bypasses RLS recursion)
CREATE OR REPLACE FUNCTION public.is_admin(user_id uuid)
RETURNS BOOLEAN AS $$
DECLARE
  is_adm BOOLEAN;
BEGIN
  IF user_id IS NULL THEN
    RETURN FALSE;
  END IF;
  SET LOCAL row_security = off;
  SELECT (role = 'admin') INTO is_adm FROM public.users WHERE id = user_id;
  RETURN COALESCE(is_adm, FALSE);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- USERS POLICIES
DROP POLICY IF EXISTS "Allow users read access" ON public.users;
CREATE POLICY "Allow users read access" ON public.users
  FOR SELECT USING (true);

DROP POLICY IF EXISTS "Allow users update own profile" ON public.users;
CREATE POLICY "Allow users update own profile" ON public.users
  FOR UPDATE USING (auth.role() = 'service_role' OR auth.uid() = id);

-- DOCUMENTS POLICIES
DROP POLICY IF EXISTS "Allow public read documents" ON public.documents;
CREATE POLICY "Allow public read documents" ON public.documents
  FOR SELECT USING (true);

DROP POLICY IF EXISTS "Allow service and admin write documents" ON public.documents;
CREATE POLICY "Allow service and admin write documents" ON public.documents
  FOR ALL USING (true);

-- CHAT HISTORY POLICIES
DROP POLICY IF EXISTS "Allow users manage own chat history" ON public.chat_history;
CREATE POLICY "Allow users manage own chat history" ON public.chat_history
  FOR ALL USING (true);

-- FAQS POLICIES
DROP POLICY IF EXISTS "Allow public read FAQs" ON public.faqs;
CREATE POLICY "Allow public read FAQs" ON public.faqs
  FOR SELECT USING (true);

DROP POLICY IF EXISTS "Allow admin manage FAQs" ON public.faqs;
CREATE POLICY "Allow admin manage FAQs" ON public.faqs
  FOR ALL USING (true);
