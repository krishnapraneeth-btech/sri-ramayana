package com.sriramayana.epic;

import android.app.Activity;
import android.content.Intent;
import android.content.res.AssetFileDescriptor;
import android.media.AudioAttributes;
import android.media.MediaPlayer;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebView;

import java.util.Locale;

public class RamayanaBridge {
    private final Activity activity;
    private final WebView webView;
    private final Handler mainHandler = new Handler(Looper.getMainLooper());

    private TextToSpeech tts;
    private volatile boolean ttsReady = false;
    private MediaPlayer bgmPlayer;
    private String currentTrack = null;

    public RamayanaBridge(Activity activity, WebView webView) {
        this.activity = activity;
        this.webView = webView;
        initTts();
    }

    private static class TtsProgressListener extends UtteranceProgressListener {
        private final RamayanaBridge bridge;

        TtsProgressListener(RamayanaBridge bridge) {
            this.bridge = bridge;
        }

        @Override
        public void onStart(String utteranceId) {}

        @Override
        public void onDone(String utteranceId) {
            if (utteranceId == null || !utteranceId.contains(":")) return;
            String[] parts = utteranceId.split(":", 2);
            try {
                final long sid = Long.parseLong(parts[0]);
                final int idx = Integer.parseInt(parts[1]);
                bridge.mainHandler.post(() -> bridge.webView.evaluateJavascript(
                        "window.__onAndroidTtsDone && window.__onAndroidTtsDone(" + sid + "," + idx + ");",
                        null
                ));
            } catch (NumberFormatException ignored) {}
        }

        @Override
        @SuppressWarnings("deprecation")
        public void onError(String utteranceId) {
            bridge.notifyTtsError(utteranceId);
        }

        @Override
        public void onError(String utteranceId, int errorCode) {
            bridge.notifyTtsError(utteranceId);
        }
    }

    private void initTts() {
        tts = new TextToSpeech(activity.getApplicationContext(), status -> {
            if (status == TextToSpeech.SUCCESS) {
                ttsReady = true;
                tts.setPitch(0.96f);
                tts.setOnUtteranceProgressListener(new TtsProgressListener(this));
            }
        });
    }

    void notifyTtsError(String utteranceId) {
        if (utteranceId == null || !utteranceId.contains(":")) return;
        String[] parts = utteranceId.split(":", 2);
        try {
            final long sid = Long.parseLong(parts[0]);
            mainHandler.post(() -> webView.evaluateJavascript(
                    "window.__onAndroidTtsError && window.__onAndroidTtsError(" + sid + ");",
                    null
            ));
        } catch (NumberFormatException ignored) {}
    }

    private Locale resolveLocale(String localeStr) {
        if (localeStr == null || localeStr.isEmpty()) return new Locale("en", "IN");
        String[] parts = localeStr.split("-");
        Locale preferred = parts.length >= 2 ? new Locale(parts[0], parts[1]) : new Locale(parts[0]);
        if (!ttsReady || tts == null) return preferred;

        int res = tts.isLanguageAvailable(preferred);
        if (res >= TextToSpeech.LANG_AVAILABLE) return preferred;

        Locale langOnly = new Locale(parts[0]);
        if (tts.isLanguageAvailable(langOnly) >= TextToSpeech.LANG_AVAILABLE) return langOnly;

        if ("en".equalsIgnoreCase(parts[0]) && tts.isLanguageAvailable(Locale.US) >= TextToSpeech.LANG_AVAILABLE) {
            return Locale.US;
        }
        return preferred;
    }

    @JavascriptInterface
    public boolean isLanguageAvailable(String localeStr) {
        if (!ttsReady || tts == null) return false;
        Locale loc = resolveLocale(localeStr);
        int res = tts.isLanguageAvailable(loc);
        return res >= TextToSpeech.LANG_AVAILABLE;
    }

    @JavascriptInterface
    public void speak(String text, String localeStr, double rate, long sessionId, int sentenceIdx) {
        if (!ttsReady || tts == null || text == null || text.trim().isEmpty()) {
            notifyTtsError(sessionId + ":" + sentenceIdx);
            return;
        }
        Locale loc = resolveLocale(localeStr);
        tts.setLanguage(loc);
        tts.setSpeechRate((float) Math.max(0.5, Math.min(2.0, rate)));
        tts.setPitch(0.96f);
        String utteranceId = sessionId + ":" + sentenceIdx;
        tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, utteranceId);
    }

    @JavascriptInterface
    public void stopSpeech() {
        if (tts != null) {
            try { tts.stop(); } catch (Exception ignored) {}
        }
    }

    @JavascriptInterface
    public void playBgm(String trackName, double volume) {
        if (trackName == null || !trackName.matches("[a-z0-9_]+")) return;
        final float clampedVol = (float) Math.max(0.0, Math.min(1.0, volume));

        mainHandler.post(() -> {
            try {
                if (trackName.equals(currentTrack) && bgmPlayer != null) {
                    bgmPlayer.setVolume(clampedVol, clampedVol);
                    if (!bgmPlayer.isPlaying()) bgmPlayer.start();
                    return;
                }
                releaseBgmInternal();
                AssetFileDescriptor afd = activity.getAssets().openFd("www/audio/" + trackName + ".mp3");
                MediaPlayer mp = new MediaPlayer();
                mp.setAudioAttributes(new AudioAttributes.Builder()
                        .setUsage(AudioAttributes.USAGE_MEDIA)
                        .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                        .build());
                mp.setDataSource(afd.getFileDescriptor(), afd.getStartOffset(), afd.getLength());
                afd.close();
                mp.setLooping(true);
                mp.setVolume(clampedVol, clampedVol);
                mp.prepare();
                mp.start();
                bgmPlayer = mp;
                currentTrack = trackName;
            } catch (Exception e) {
                releaseBgmInternal();
            }
        });
    }

    @JavascriptInterface
    public void setBgmVolume(double volume) {
        final float clampedVol = (float) Math.max(0.0, Math.min(1.0, volume));
        mainHandler.post(() -> {
            if (bgmPlayer != null) {
                try { bgmPlayer.setVolume(clampedVol, clampedVol); } catch (Exception ignored) {}
            }
        });
    }

    @JavascriptInterface
    public void pauseBgm() {
        mainHandler.post(() -> {
            if (bgmPlayer != null) {
                try {
                    if (bgmPlayer.isPlaying()) bgmPlayer.pause();
                } catch (Exception ignored) {}
            }
        });
    }

    @JavascriptInterface
    public void stopBgm() {
        mainHandler.post(this::releaseBgmInternal);
    }

    private void releaseBgmInternal() {
        currentTrack = null;
        if (bgmPlayer != null) {
            try {
                if (bgmPlayer.isPlaying()) bgmPlayer.stop();
                bgmPlayer.release();
            } catch (Exception ignored) {}
            bgmPlayer = null;
        }
    }

    @JavascriptInterface
    public void setKeepScreenOn(boolean keepOn) {
        mainHandler.post(() -> {
            if (keepOn) {
                activity.getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
            } else {
                activity.getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
            }
        });
    }

    @JavascriptInterface
    public void openTtsSettings() {
        mainHandler.post(() -> {
            try {
                Intent intent = new Intent("com.android.settings.TTS_SETTINGS");
                intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                activity.startActivity(intent);
            } catch (Exception e) {
                try {
                    Intent fallback = new Intent(Settings.ACTION_SETTINGS);
                    fallback.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    activity.startActivity(fallback);
                } catch (Exception ignored) {}
            }
        });
    }

    public void onPause() {
        stopSpeech();
        if (bgmPlayer != null) {
            try {
                if (bgmPlayer.isPlaying()) bgmPlayer.pause();
            } catch (Exception ignored) {}
        }
    }

    public void destroy() {
        stopSpeech();
        if (tts != null) {
            try { tts.shutdown(); } catch (Exception ignored) {}
            tts = null;
        }
        releaseBgmInternal();
    }
}
