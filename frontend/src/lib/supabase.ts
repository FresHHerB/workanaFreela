import { createClient } from '@supabase/supabase-js';
import type { ProjetoFreela } from '../types';

// Configurações do Supabase - TEMPORÁRIO: hardcoded para testar
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://ueblczslrbntowjacqgq.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVlYmxjenNscmJudG93amFjcWdxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4MDMwODgsImV4cCI6MjA2NzM3OTA4OH0.LH6E3vq3Qtrx8_9A9WvhJRTi6ANsFtcoFS4wwjGY4zk';

console.log('Supabase Config Debug:', {
  url: supabaseUrl ? 'SET' : 'MISSING',
  key: supabaseAnonKey ? 'SET' : 'MISSING',
  fullUrl: supabaseUrl,
  usingFallback: !import.meta.env.VITE_SUPABASE_URL
});

if (!supabaseUrl || !supabaseAnonKey) {
  const errorMsg = `Missing Supabase environment variables. URL: ${supabaseUrl ? 'SET' : 'MISSING'}, KEY: ${supabaseAnonKey ? 'SET' : 'MISSING'}`;
  console.error(errorMsg);
  throw new Error(errorMsg);
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export const fetchProjetos = async (): Promise<ProjetoFreela[]> => {
  const { data, error } = await supabase
    .from('projetos_freela')
    .select('*');

  if (error) {
    console.error('Erro ao buscar projetos:', error);
    return [];
  }

  return data || [];
};