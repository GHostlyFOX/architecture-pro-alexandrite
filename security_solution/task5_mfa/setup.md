# Setting up MFA in Keycloak

To enable Multi-Factor Authentication (OTP) for BionicPRO users:

1.  **Log in to Keycloak Admin Console.**
2.  **Select the Realm** (e.g., `bionicpro`).
3.  **Navigate to Authentication** (in the left menu).
4.  **Flows Tab:**
    *   Select `Browser` flow.
    *   Copy the flow (e.g., name it `Browser with MFA`).
    *   In the new flow, find the "OTP" or "Conditional OTP" execution.
    *   Set the requirement to `REQUIRED` (or `ALTERNATIVE` if combined with other factors, but task asks for mandatory).
    *   **Recommendation:** Usually, you create a sub-flow "MFA" containing "OTP Form" and set it to `REQUIRED`.
5.  **Bindings Tab:**
    *   Set the "Browser Flow" to your new `Browser with MFA`.
6.  **Navigate to Authentication > Policies > OTP Policy:**
    *   Configure the algorithm (TOTP).
    *   Period: 30 seconds.
    *   Supported Applications: Google Authenticator, FreeOTP.
7.  **User Experience:**
    *   When a user logs in next time, they will be prompted to set up OTP by scanning a QR code.
    *   Subsequent logins will require the code.
