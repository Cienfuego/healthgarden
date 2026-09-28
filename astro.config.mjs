// @ts-check
import { defineConfig } from 'astro/config';

import tailwindcss from '@tailwindcss/vite';

import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://healthgardenadvocacy.com',
  build: {
    format: 'file',
  },

  vite: {
    plugins: [tailwindcss()]
  },
  integrations: [
    sitemap({
      filter: (page) => !page.includes('/404'),
      serialize: (item) => {
        if (item.url.endsWith('/')) return item;
        return { ...item, url: item.url + '.html' };
      },
    })
  ]
});
