import { Html, Head, Main, NextScript } from 'next/document'

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        {/* Mobile optimization */}
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5, user-scalable=yes" />
        <meta name="theme-color" content="#2563eb" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="NYC Zoning Platform" />
        <meta name="format-detection" content="telephone=no" />
        <meta name="mobile-web-app-capable" content="yes" />

        {/* Performance and security */}
        <link rel="dns-prefetch" href="//api.mapbox.com" />
        <link rel="preconnect" href="https://api.mapbox.com" crossOrigin="" />

        {/* Browser compatibility */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              // Polyfill for older browsers
              if (!window.fetch) {
                // Load fetch polyfill for IE11
                document.write('<script src="https://cdn.jsdelivr.net/npm/whatwg-fetch@3.6.2/fetch.min.js"><\\/script>');
              }
            `,
          }}
        />

        {/* CSS custom properties for older browser support */}
        <style>{`
          /* Ensure consistent box-sizing */
          *, *::before, *::after {
            box-sizing: border-box;
          }

          /* Fix for iOS Safari zoom on input focus */
          @media screen and (max-width: 768px) {
            input[type="text"],
            input[type="email"],
            input[type="password"],
            textarea,
            select {
              font-size: 16px !important;
            }
          }

          /* Smooth scrolling for better UX */
          html {
            scroll-behavior: smooth;
          }

          /* Hide scrollbar on mobile for cleaner look */
          @media screen and (max-width: 768px) {
            ::-webkit-scrollbar {
              display: none;
            }
            * {
              -ms-overflow-style: none;
              scrollbar-width: none;
            }
          }
        `}</style>

        {/* Mapbox GL CSS */}
        <link
          href="https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.css"
          rel="stylesheet"
        />

        {/* Favicon and icons */}
        <link rel="icon" type="image/svg+xml" href="/logo.svg" />
        <link rel="apple-touch-icon" href="/logo.svg" />
        <link rel="icon" type="image/svg+xml" sizes="any" href="/logo.svg" />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  )
}