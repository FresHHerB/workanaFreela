import { createClient } from '@supabase/supabase-js';
import type { ProjetoFreela } from '../types';

// Configurações do Supabase via variáveis de ambiente
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

console.log('Supabase Config Debug:', {
  url: supabaseUrl ? 'SET' : 'MISSING',
  key: supabaseAnonKey ? 'SET' : 'MISSING',
  fullUrl: supabaseUrl
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