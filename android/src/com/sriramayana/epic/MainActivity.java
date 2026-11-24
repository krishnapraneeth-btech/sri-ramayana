package com.sriramayana.epic;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.res.AssetManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import java.io.InputStream;

public class MainActivity extends Activity {
    private static final String ASSET_HOST = "appassets.androidplatform.net";
    private WebView webView;
    private RamayanaBridge bridge;

    private static class LocalWebViewClient extends WebViewClient {
        private final AssetManager assets;

        LocalWebViewClient(AssetManager assets) {
            this.assets = assets;
        }

        @Override
        public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
            Uri uri = request.getUrl();
            if (ASSET_HOST.equals(uri.getHost())) {
                String path = uri.getPath();
                if (path == null || path.equals("/")) path = "/www/index.html";
                if (path.startsWith("/")) path = path.substring(1);
                if (!path.startsWith("www/")) path = "www/" + path;
                try {
                    InputStream is = assets.open(path);
                    return new WebResourceResponse(guessMimeType(path), "UTF-8", is);
                } catch (Exception e) {
                    return new WebResourceResponse("text/plain", "UTF-8", 404, "Not Found", null, null);
                }
            }
            return super.shouldInterceptRequest(view, request);
        }

        @Override
        public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
            Uri uri = request.getUrl();
            return !ASSET_HOST.equals(uri.getHost());
        }

        private String guessMimeType(String path) {
            String lower = path.toLowerCase();
            if (lower.endsWith(".html")) return "text/html";
            if (lower.endsWith(".js")) return "application/javascript";
            if (lower.endsWith(".css")) return "text/css";
            if (lower.endsWith(".jpg") || lower.endsWith(".jpeg")) return "image/jpeg";
            if (lower.endsWith(".png")) return "image/png";
            if (lower.endsWith(".svg")) return "image/svg+xml";
            if (lower.endsWith(".mp3")) return "audio/mpeg";
            if (lower.endsWith(".json")) return "application/json";
            return "application/octet-stream";
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        getWindow().setStatusBarColor(Color.parseColor("#090811"));
        getWindow().setNavigationBarColor(Color.parseColor("#090811"));

        webView = new WebView(this);
        webView.setBackgroundColor(Color.parseColor("#090811"));
        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);

        bridge = new RamayanaBridge(this, webView);
        webView.addJavascriptInterface(bridge, "RamayanaNative");
        webView.setWebViewClient(new LocalWebViewClient(getAssets()));
        webView.loadUrl("https://" + ASSET_HOST + "/www/index.html");
    }

    @Override
    @SuppressWarnings("deprecation")
    public void onBackPressed() {
        if (webView != null) {
            webView.evaluateJavascript(
                "(function(){var p=document.getElementById('playerView');if(p&&!p.classList.contains('hidden')){document.getElementById('backHomeBtn').click();return true;}return false;})()",
                result -> {
                    if (!"true".equals(result)) {
                        MainActivity.super.onBackPressed();
                    }
                }
            );
            return;
        }
        super.onBackPressed();
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (webView != null) {
            webView.evaluateJavascript("window.__onAndroidAppPause && window.__onAndroidAppPause();", null);
            webView.onPause();
        }
        if (bridge != null) {
            bridge.onPause();
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (webView != null) {
            webView.onResume();
        }
    }

    @Override
    protected void onDestroy() {
        if (bridge != null) {
            bridge.destroy();
        }
        if (webView != null) {
            webView.destroy();
        }
        super.onDestroy();
    }
}
