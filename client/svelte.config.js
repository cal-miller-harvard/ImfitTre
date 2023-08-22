import adapter from '@sveltejs/adapter-static';
 
export default {
  // kit: {
  //   prerender: { entries: [] }, // disable prerender
  //   adapter: adapter({
  //       fallback: "index.html",
  //   }),
  //   paths: {
  //     base: '',
  //   },
  // }
  kit: {
    adapter: adapter({
      // default options are shown. On some platforms
      // these options are set automatically — see below
      pages: 'build',
      assets: 'build',
      fallback: 'index.html',
      precompress: false,
      strict: true
    })
  }
};