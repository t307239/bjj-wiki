/**
 * Amazon Country Detection & Link Redirect
 * Detects language from URL path and provides country-specific Amazon links
 */

(function() {
  // Detect language from URL path
  const pathname = window.location.pathname;
  let lang = 'en';
  let amazonDomain = 'amazon.com';

  if (pathname.includes('/ja/')) {
    lang = 'ja';
    amazonDomain = 'amazon.co.jp';
  } else if (pathname.includes('/pt/')) {
    lang = 'pt';
    amazonDomain = 'amazon.com.br';
  } else {
    lang = 'en';
    amazonDomain = 'amazon.com';
  }

  window.bjjAmazonConfig = {
    lang: lang,
    domain: amazonDomain,
    affiliate: 'bjj06-22'
  };

  // Product mapping by language
  const PRODUCT_LINKS = {
    'en': {
      'bjj-gi': `https://${amazonDomain}/s?k=judo+gi&tag=bjj06-22`,
      'fuji-gi': `https://${amazonDomain}/s?k=fuji+judo+gi&tag=bjj06-22`,
      'scramble-gi': `https://${amazonDomain}/s?k=scramble+judo+gi&tag=bjj06-22`,
      'bjj-instructional': `https://${amazonDomain}/s?k=brazilian+jiu+jitsu+instructional&tag=bjj06-22`,
      'saulo-book': `https://${amazonDomain}/s?k=jiu-jitsu+university+saulo+ribeiro&tag=bjj06-22`,
      'bjj-book': `https://${amazonDomain}/s?k=brazilian+jiu+jitsu+book&tag=bjj06-22`,
      'bjj-mat': `https://${amazonDomain}/s?k=judo+mat+home&tag=bjj06-22`,
      'bjj-dummy': `https://${amazonDomain}/s?k=grappling+dummy+heavy+bag&tag=bjj06-22`,
    },
    'ja': {
      'bjj-gi': `https://${amazonDomain}/s?k=柔道着&tag=bjj06-22`,
      'fuji-gi': `https://${amazonDomain}/s?k=FUJI+柔道着&tag=bjj06-22`,
      'scramble-gi': `https://${amazonDomain}/s?k=SCRAMBLE+柔道着&tag=bjj06-22`,
      'bjj-instructional': `https://${amazonDomain}/s?k=ブラジリアン柔術+教則+DVD&tag=bjj06-22`,
      'saulo-book': `https://${amazonDomain}/s?k=Jiu-Jitsu+University+サウロ&tag=bjj06-22`,
      'bjj-book': `https://${amazonDomain}/s?k=ブラジリアン柔術+本&tag=bjj06-22`,
      'bjj-mat': `https://${amazonDomain}/s?k=柔道マット+ホーム&tag=bjj06-22`,
      'bjj-dummy': `https://${amazonDomain}/s?k=グラップリングダミー&tag=bjj06-22`,
    },
    'pt': {
      'bjj-gi': `https://${amazonDomain}/s?k=kimono+judo&tag=bjj06-22`,
      'fuji-gi': `https://${amazonDomain}/s?k=FUJI+kimono+judo&tag=bjj06-22`,
      'scramble-gi': `https://${amazonDomain}/s?k=SCRAMBLE+kimono+judo&tag=bjj06-22`,
      'bjj-instructional': `https://${amazonDomain}/s?k=jiu-jitsu+brasileiro+aula+dvd&tag=bjj06-22`,
      'saulo-book': `https://${amazonDomain}/s?k=jiu-jitsu+university+saulo&tag=bjj06-22`,
      'bjj-book': `https://${amazonDomain}/s?k=jiu-jitsu+brasileiro+livro&tag=bjj06-22`,
      'bjj-mat': `https://${amazonDomain}/s?k=tapete+judo+casa&tag=bjj06-22`,
      'bjj-dummy': `https://${amazonDomain}/s?k=boneco+grappling&tag=bjj06-22`,
    }
  };

  // Global function to get Amazon link
  window.getAmazonLink = function(productKey) {
    const langLinks = PRODUCT_LINKS[lang] || PRODUCT_LINKS['en'];
    return langLinks[productKey] || `https://${amazonDomain}/s?k=judo&tag=bjj06-22`;
  };

  // Replace amazon.com generic links with smart redirect
  document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('a[href*="amazon.com"]');
    links.forEach(link => {
      const href = link.getAttribute('href');

      // Skip if already has affiliate tag or country domain
      if (href.includes('tag=') || href.includes('amazon.co.jp') || href.includes('amazon.com.br')) {
        return;
      }

      // Replace domain with country-specific one
      const newHref = href.replace('amazon.com', amazonDomain).replace(/([?&])tag=[^&]*/g, '').replace(/\?$/, '');

      // Add affiliate tag
      const separator = newHref.includes('?') ? '&' : '?';
      link.setAttribute('href', newHref + separator + 'tag=bjj06-22');
    });
  });
})();
