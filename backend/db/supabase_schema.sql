-- Supabase/Postgres schema for Hermes cloud storage, models, backtests, and training jobs
-- Run this in the Supabase SQL editor or via psql/supabase cli.
-- Date: 2025-09-23

-- Extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Helpful note:
-- Supabase exposes the current user's id via auth.uid() and JWT claims via
-- current_setting('jwt.claims.role', true). Policies below use these helpers.

-- ---------------------------------------------
-- Types
-- ---------------------------------------------
CREATE TYPE job_status AS ENUM ('queued','running','completed','failed','cancelled');

-- ---------------------------------------------
-- Files metadata (linking to Supabase Storage objects)
-- ---------------------------------------------
CREATE TABLE IF NOT EXISTS public.files_metadata (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  bucket text NOT NULL,
  path text NOT NULL,
  name text,
  -- Optional admin-entered listing features (e.g., tags, categories, flags)
  features jsonb DEFAULT '{}'::jsonb,
  size_bytes bigint,
  content_type text,
  metadata jsonb DEFAULT '{}'::jsonb,
  uploaded_by uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  is_public boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE UNIQUE INDEX ON public.files_metadata (bucket, path);
CREATE INDEX ON public.files_metadata (uploaded_by);
CREATE INDEX ON public.files_metadata USING gin (metadata jsonb_path_ops);

-- trigger to update updated_at
CREATE OR REPLACE FUNCTION public.fn_files_metadata_updated_at()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_files_metadata_updated_at
BEFORE UPDATE ON public.files_metadata
FOR EACH ROW EXECUTE FUNCTION public.fn_files_metadata_updated_at();

-- ---------------------------------------------
-- Models (trained artifacts)
-- ---------------------------------------------
CREATE TABLE IF NOT EXISTS public.models (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  -- Optional admin-entered listing features for models
  features jsonb DEFAULT '{}'::jsonb,
  description text,
  file_id uuid REFERENCES public.files_metadata(id) ON DELETE SET NULL,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_by uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE INDEX ON public.models (created_by);
CREATE INDEX ON public.models USING gin (metadata jsonb_path_ops);
CREATE INDEX ON public.models USING gin (features jsonb_path_ops);

CREATE OR REPLACE FUNCTION public.fn_models_updated_at()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_models_updated_at
BEFORE UPDATE ON public.models
FOR EACH ROW EXECUTE FUNCTION public.fn_models_updated_at();

-- ---------------------------------------------
-- Training jobs and history
-- ---------------------------------------------
CREATE TABLE IF NOT EXISTS public.training_jobs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  model_id uuid REFERENCES public.models(id) ON DELETE SET NULL,
  created_by uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  status job_status NOT NULL DEFAULT 'queued',
  params jsonb DEFAULT '{}'::jsonb,
  metrics jsonb DEFAULT '{}'::jsonb,
  logs text,
  started_at timestamptz,
  finished_at timestamptz,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX ON public.training_jobs (created_by);
CREATE INDEX ON public.training_jobs (status);
CREATE INDEX ON public.training_jobs USING gin (params jsonb_path_ops);

-- Notify channel on status changes to facilitate real-time UI updates
CREATE OR REPLACE FUNCTION public.notify_training_job_update()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
  payload text;
BEGIN
  payload := row_to_json(NEW)::text;
  PERFORM pg_notify('training_jobs', payload);
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_training_jobs_notify
AFTER INSERT OR UPDATE ON public.training_jobs
FOR EACH ROW EXECUTE FUNCTION public.notify_training_job_update();

-- ---------------------------------------------
-- Backtests and trades
-- ---------------------------------------------
CREATE TABLE IF NOT EXISTS public.backtests (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text,
  symbol text NOT NULL,
  timeframe text DEFAULT '1d',
  start_date date NOT NULL,
  end_date date NOT NULL,
  initial_balance numeric(18,6) DEFAULT 100000.0,
  final_balance numeric(18,6),
  metrics jsonb DEFAULT '{}'::jsonb,
  created_by uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX ON public.backtests (created_by);
CREATE INDEX ON public.backtests (symbol);
CREATE INDEX ON public.backtests USING gin (metrics jsonb_path_ops);

CREATE TABLE IF NOT EXISTS public.backtest_trades (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  backtest_id uuid REFERENCES public.backtests(id) ON DELETE CASCADE,
  timestamp timestamptz NOT NULL,
  symbol text NOT NULL,
  side text NOT NULL,
  qty numeric(24,8) NOT NULL,
  price numeric(18,6) NOT NULL,
  pnl numeric(18,6) DEFAULT 0,
  meta jsonb DEFAULT '{}'::jsonb
);

CREATE INDEX ON public.backtest_trades (backtest_id);
CREATE INDEX ON public.backtest_trades (symbol);
CREATE INDEX ON public.backtest_trades USING gin (meta jsonb_path_ops);

-- Convenience function to recalc summary metrics for a backtest
CREATE OR REPLACE FUNCTION public.fn_recalc_backtest_metrics(b_id uuid)
RETURNS jsonb LANGUAGE plpgsql AS $$
DECLARE
  tot_pl numeric := 0;
  wins int := 0;
  losses int := 0;
  trades int := 0;
  max_dd numeric := 0;
  equity numeric := 0;
  eq_cur jsonb := '[]'::jsonb;
BEGIN
  SELECT COALESCE(SUM(pnl),0), COUNT(*) INTO tot_pl, trades FROM public.backtest_trades WHERE backtest_id = b_id;
  SELECT COUNT(*) FILTER (WHERE pnl > 0), COUNT(*) FILTER (WHERE pnl <= 0) INTO wins, losses FROM public.backtest_trades WHERE backtest_id = b_id;

  -- Build a simple equity curve (cumulative pnl)
  eq_cur := (
    SELECT jsonb_agg(row_to_json(t)) FROM (
      SELECT timestamp, sum(pnl) OVER (ORDER BY timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_pnl
      FROM public.backtest_trades WHERE backtest_id = b_id ORDER BY timestamp
    ) t
  );

  RETURN jsonb_build_object(
    'total_pnl', tot_pl,
    'trades', trades,
    'wins', wins,
    'losses', losses,
    'win_rate', CASE WHEN trades > 0 THEN (wins::numeric / trades) ELSE 0 END,
    'equity_curve', eq_cur
  );
END;
$$;

-- Trigger to update backtest.metrics when trades change
CREATE OR REPLACE FUNCTION public.fn_update_backtest_metrics()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  UPDATE public.backtests SET metrics = public.fn_recalc_backtest_metrics(NEW.backtest_id), final_balance = COALESCE(final_balance, initial_balance) + (public.fn_recalc_backtest_metrics(NEW.backtest_id)->>'total_pnl')::numeric WHERE id = NEW.backtest_id;
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_backtest_trade_update
AFTER INSERT OR UPDATE ON public.backtest_trades
FOR EACH ROW EXECUTE FUNCTION public.fn_update_backtest_metrics();

-- ---------------------------------------------
-- Row-level security policies
-- ---------------------------------------------
-- Enable RLS where appropriate
ALTER TABLE public.files_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.models ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.training_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.backtests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.backtest_trades ENABLE ROW LEVEL SECURITY;

-- Helper: allow service role (server-side) access via jwt.claims
-- Note: Supabase server-side operations use the 'service_role' JWT claim.

-- Files: owners and service role can full-access; public objects selectable when is_public = true
CREATE POLICY "files_owner_or_service" ON public.files_metadata
  USING (
    (current_setting('jwt.claims.role', true) = 'service_role')
    OR (auth.uid() = uploaded_by)
    OR (is_public = true AND (current_setting('jwt.claims.role', true) IS NULL)) -- public read for anon without JWT role
  )
  WITH CHECK (
    (current_setting('jwt.claims.role', true) = 'service_role') OR (auth.uid() = uploaded_by)
  );

-- Models: owner + service role
CREATE POLICY "models_owner_or_service" ON public.models
  USING (
    (current_setting('jwt.claims.role', true) = 'service_role') OR (auth.uid() = created_by)
  )
  WITH CHECK (
    (current_setting('jwt.claims.role', true) = 'service_role') OR (auth.uid() = created_by)
  );

-- Training jobs: owners can view their jobs; service role can view all
CREATE POLICY "training_jobs_owner_or_service" ON public.training_jobs
  USING (
    (current_setting('jwt.claims.role', true) = 'service_role') OR (auth.uid() = created_by)
  )
  WITH CHECK (
    (current_setting('jwt.claims.role', true) = 'service_role') OR (auth.uid() = created_by)
  );

-- Backtests: owners only by default
CREATE POLICY "backtests_owner_or_service" ON public.backtests
  USING (
    (current_setting('jwt.claims.role', true) = 'service_role') OR (auth.uid() = created_by)
  )
  WITH CHECK (
    (current_setting('jwt.claims.role', true) = 'service_role') OR (auth.uid() = created_by)
  );

-- Trades inherit backtest's protections; allow inserts done by service role or job processes only
CREATE POLICY "backtest_trades_insert_by_service_or_owner" ON public.backtest_trades
  FOR INSERT
  WITH CHECK (
    (current_setting('jwt.claims.role', true) = 'service_role')
    OR EXISTS (SELECT 1 FROM public.backtests b WHERE b.id = NEW.backtest_id AND b.created_by = auth.uid())
  );

CREATE POLICY "backtest_trades_select_owner_or_service" ON public.backtest_trades
  USING (
    (current_setting('jwt.claims.role', true) = 'service_role')
    OR EXISTS (SELECT 1 FROM public.backtests b WHERE b.id = public.backtest_trades.backtest_id AND b.created_by = auth.uid())
  );

-- ---------------------------------------------
-- Admin-managed listing features
-- ---------------------------------------------
CREATE TABLE IF NOT EXISTS public.listing_features (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  slug text UNIQUE NOT NULL,
  description text,
  meta jsonb DEFAULT '{}'::jsonb,
  created_by uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE INDEX ON public.listing_features (slug);
CREATE INDEX ON public.listing_features USING gin (meta jsonb_path_ops);

CREATE OR REPLACE FUNCTION public.fn_listing_features_updated_at()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_listing_features_updated_at
BEFORE UPDATE ON public.listing_features
FOR EACH ROW EXECUTE FUNCTION public.fn_listing_features_updated_at();

-- Enable RLS for admin-managed features
ALTER TABLE public.listing_features ENABLE ROW LEVEL SECURITY;

-- Only service_role or members of 'admin' role (via JWT claim) can insert/update/delete
CREATE POLICY "listing_features_admin_only" ON public.listing_features
  USING (
    (current_setting('jwt.claims.role', true) = 'service_role')
    OR (current_setting('jwt.claims.role', true) = 'admin')
  )
  WITH CHECK (
    (current_setting('jwt.claims.role', true) = 'service_role')
    OR (current_setting('jwt.claims.role', true) = 'admin')
  );

-- Read access: service_role or any authenticated user can read listings
CREATE POLICY "listing_features_read" ON public.listing_features
  FOR SELECT
  USING (
    (current_setting('jwt.claims.role', true) = 'service_role') OR auth.uid() IS NOT NULL
  );


-- ---------------------------------------------
-- Grants (optional): give anon/select access to files marked public
-- You can tune these grants per your application's needs
GRANT SELECT ON public.files_metadata TO anon;

-- ---------------------------------------------
-- Convenience views and helper queries
-- ---------------------------------------------
CREATE OR REPLACE VIEW public.view_user_models AS
SELECT m.*, f.bucket AS file_bucket, f.path AS file_path
FROM public.models m
LEFT JOIN public.files_metadata f ON f.id = m.file_id;

-- ---------------------------------------------
-- Example usage notes
-- ---------------------------------------------
-- 1) Apply this SQL in Supabase SQL Editor or via the CLI:
--    supabase db query < backend/db/supabase_schema.sql

-- 2) Upload a file to Supabase Storage (e.g. models/model_v1.pkl) and insert metadata:
--    INSERT INTO public.files_metadata (bucket, path, name, size_bytes, content_type, uploaded_by, is_public)
--    VALUES ('models','models/model_v1.pkl','model_v1.pkl', 12345, 'application/octet-stream', '00000000-0000-0000-0000-000000000000', false);

-- 3) Create a model record referencing that file:
--    INSERT INTO public.models (name, description, file_id, created_by)
--    VALUES ('finbert-v1','Sentiment model for news', '<file-uuid>', auth.uid());

-- 4) Start a training job (from backend service or authenticated user):
--    INSERT INTO public.training_jobs (model_id, created_by, params, status) VALUES ('<model-uuid>', auth.uid(), '{"epochs":3}', 'queued');

-- ---------------------------------------------
-- End of schema
-- ---------------------------------------------
