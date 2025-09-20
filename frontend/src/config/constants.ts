/**
 * Application constants and configuration
 */

export const API_ENDPOINTS = {
  HEALTH: '/api/health',
  SCRAPE: '/api/scrape',
} as const;

export const REFRESH_INTERVALS = {
  AUTO_REFRESH: 30000, // 30 seconds
  SCRAPE_DELAY: 2000,  // 2 seconds delay after scrape
} as const;

export const UI_CONSTANTS = {
  ITEMS_PER_PAGE: 50,
  ANIMATION_DURATION: 200,
} as const;