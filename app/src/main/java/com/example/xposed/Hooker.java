package com.example.xposed;

import android.util.Log;

import de.robv.android.xposed.IXposedHookLoadPackage;
import de.robv.android.xposed.callbacks.XC_LoadPackage;

public class Hooker implements IXposedHookLoadPackage {

    @Override
    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam loadPackageParam) throws Throwable {
        Hook();
    }

    private void Hook() {
        Log("Hooked!");
    }

    private void Log(String msg) {
        Log.v("Xposed",msg);
    }
}
