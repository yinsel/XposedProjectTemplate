package com.example.xposed.demo

import org.junit.Assert.assertEquals
import org.junit.Test

class GreetingProviderTest {
    @Test
    fun targetRetainsItsReflectiveSignatureAndUnhookedResult() {
        val method = GreetingProvider::class.java.getDeclaredMethod("greeting")
        assertEquals(String::class.java, method.returnType)
        assertEquals("Hello from the demo app.", method.invoke(GreetingProvider()))
    }
}
