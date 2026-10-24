plugins { alias(libs.plugins.android.application) }

android {
    namespace = "com.example.xposed.demo"
    compileSdk = 37
    defaultConfig {
        applicationId = "com.example.xposed.demo"
        minSdk = 26
        targetSdk = 37
        versionCode = 1
        versionName = "1.0.0"
    }
    // 不混淆或内联测试靶点，便于 JADX 分析和设备验收。
    buildTypes { release { isMinifyEnabled = false } }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    lint { abortOnError = true }
}

dependencies { testImplementation(libs.junit) }
