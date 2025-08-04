"""
Browser console script to extract working ClubOS authentication tokens
Run this in your browser console while you're logged into ClubOS
"""

# Copy and paste this into your browser console while logged into ClubOS:
# (Open DevTools -> Console tab -> paste and press Enter)

browser_script = """
// Extract all cookies and tokens from current ClubOS session
console.log('🔧 Extracting ClubOS authentication data...');

// Get all cookies
let cookies = {};
document.cookie.split(';').forEach(cookie => {
    let [name, value] = cookie.trim().split('=');
    if (name && value) {
        cookies[name] = value;
    }
});

// Extract tokens from page
let tokens = {};

// Look for fingerprint and source tokens in forms
document.querySelectorAll('input[name="__fp"]').forEach(input => {
    tokens['__fp'] = input.value;
});

document.querySelectorAll('input[name="_sourcePage"]').forEach(input => {
    tokens['_sourcePage'] = input.value;
});

// Look for JavaScript variables with tokens
if (window.apiV3AccessToken) tokens['jsApiV3AccessToken'] = window.apiV3AccessToken;
if (window.apiV3RefreshToken) tokens['jsApiV3RefreshToken'] = window.apiV3RefreshToken;
if (window.loggedInUserId) tokens['jsLoggedInUserId'] = window.loggedInUserId;

// Extract from script tags
document.querySelectorAll('script').forEach(script => {
    if (script.textContent) {
        // Look for token assignments
        let fpMatch = script.textContent.match(/["']__fp["']\\s*:\\s*["']([^"']+)["']/);
        if (fpMatch) tokens['scriptFp'] = fpMatch[1];
        
        let sourceMatch = script.textContent.match(/["']_sourcePage["']\\s*:\\s*["']([^"']+)["']/);
        if (sourceMatch) tokens['scriptSourcePage'] = sourceMatch[1];
        
        let userIdMatch = script.textContent.match(/loggedInUserId["']\\s*:\\s*["']?([^"',}]+)["']?/);
        if (userIdMatch) tokens['scriptUserId'] = userIdMatch[1];
    }
});

// Output the data
console.log('📊 Cookies:', cookies);
console.log('🔑 Tokens:', tokens);
console.log('🌐 Current URL:', window.location.href);
console.log('📋 Session Storage:', {...sessionStorage});
console.log('💾 Local Storage:', {...localStorage});

// Create formatted output for easy copying
let authData = {
    timestamp: new Date().toISOString(),
    url: window.location.href,
    cookies: cookies,
    tokens: tokens,
    sessionStorage: {...sessionStorage},
    localStorage: {...localStorage}
};

console.log('\\n🎯 COPY THIS DATA TO UPDATE THE SCRIPT:');
console.log('='.repeat(50));
console.log(JSON.stringify(authData, null, 2));
console.log('='.repeat(50));

// Also save to clipboard if possible
if (navigator.clipboard) {
    navigator.clipboard.writeText(JSON.stringify(authData, null, 2)).then(() => {
        console.log('✅ Auth data copied to clipboard!');
    }).catch(() => {
        console.log('⚠️ Could not copy to clipboard, please copy manually');
    });
}
"""

print("🌐 BROWSER CONSOLE SCRIPT")
print("=" * 60)
print("1. Open ClubOS in your browser")
print("2. Make sure you're logged in and can access training pages")
print("3. Open DevTools (F12)")
print("4. Go to Console tab")
print("5. Copy and paste the script below:")
print("=" * 60)
print()
print(browser_script)
print()
print("=" * 60)
print("6. Press Enter to run the script")
print("7. Copy the JSON output and paste it into a new file called 'fresh_tokens.json'")
print("8. I'll update the authentication script to use the fresh tokens")
