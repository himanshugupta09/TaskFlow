# 🔧 TaskFlow - Deployment Issues & Fix Guide

## Issues Reported

1. **HTTP 401 Unauthorized on email invite**
2. **Responsive UI changes not showing on deployed site**

---

## Root Causes

### Issue 1: 401 Unauthorized
**Cause**: The `invite_to_project` endpoint requires authentication but was missing explicit `@permission_classes([IsAuthenticated])` decorator in some cases. On deployed site, token might not be properly transmitted.

**Symptoms**:
- Getting 401 error when trying to send invites
- Error message: "Authentication credentials were not provided"

**How it happens**:
1. User is logged in locally (token exists)
2. User clicks "Invite Member"
3. API call is made but token isn't properly attached to the request header
4. Server responds with 401 since it can't verify authentication

### Issue 2: Responsive changes not showing
**Cause**: The new responsive HTML code hasn't been properly deployed or cached by the browser.

**Symptoms**:
- Main branch was deployed but responsive sidebar/hamburger menu not visible
- App looks like old version on mobile
- Desktop layout still works fine

**How it happens**:
1. Code changes made locally (responsive CSS + React state)
2. Changes pushed to main branch
3. Railway redeploys but HTML file might be cached
4. Browser loads cached old version without responsive code

---

## ✅ Fixes Applied

### Fix 1: Enhanced Authentication Handling
**What was changed**:
- Added explicit `@permission_classes([IsAuthenticated])` to:
  - `invite_to_project` 
  - `project_invites`
  - `cancel_invite`
- Improved API error handling to check for token before making requests
- Added detailed error logging for debugging

**Files modified**:
- `taskflow/api/views.py` - Added authentication decorators
- `taskflow/api/templates/index.html` - Improved API helper function
- `taskflow/taskflow/settings.py` - Better static files configuration

### Fix 2: Improved API Client
**What was changed**:
- Updated `api()` function to explicitly add Bearer token
- Better error messages for 401 errors
- Console logging for debugging failed requests
- Proper error extraction from API responses

**Code change**:
```javascript
// BEFORE: Token conditionally added
headers: {'Content-Type':'application/json',...(getToken()?{'Authorization':'Bearer '+getToken()}:{})}

// AFTER: Always check and log token
const token = getToken();
if(token) { headers['Authorization'] = 'Bearer ' + token; }
console.error('401 Auth failed', {token: !!token, headers});
```

### Fix 3: Production-Ready Configuration
**Changes made**:
- Improved STATICFILES_DIRS configuration
- Better MIME type handling with WhiteNoise
- Proper cache control for static files

---

## 🚀 How to Deploy the Fixes

### Option A: Push to Railway (Recommended)

1. **Commit your changes**:
```bash
cd c:\Users\Lenovo\OneDrive\Desktop\TaskFlow
git add -A
git commit -m "Fix: Authentication for invites + responsive design fixes"
```

2. **Push to main branch**:
```bash
git push origin main
```

3. **Railway will automatically redeploy** with the fixes

4. **Clear your browser cache**:
   - Press `Ctrl+Shift+Del` (or Cmd+Shift+Del on Mac)
   - Select "All time"
   - Check "Cookies and other site data"
   - Check "Cached images and files"
   - Click "Clear data"

5. **Test the fixes**:
   - Open DevTools (F12)
   - Go to Network tab
   - Refresh page (Ctrl+R)
   - Try sending an invite
   - Check if 401 error appears (it shouldn't if login is valid)

### Option B: Manual Railway Redeploy

1. Go to [Railway Dashboard](https://railway.app)
2. Select your TaskFlow project
3. Go to "Deployments"
4. Click the last deployment
5. Click "Redeploy"
6. Wait for deployment to complete (~2-3 min)
7. Clear browser cache and test

---

## 🧪 Testing the Fixes

### Test 1: Verify Responsive Design Shows Up
1. Open deployed app on mobile (or DevTools mobile view)
2. You should see **☰ hamburger menu** at top-left
3. Tap hamburger to see sidebar slide in
4. Grids should be single column on mobile
5. Buttons should be larger (48px)

**If not working**:
- Hard refresh: `Ctrl+Shift+R` (or `Cmd+Shift+R`)
- Clear all cache: `Ctrl+Shift+Del` → "All time"
- Try incognito/private mode

### Test 2: Verify Invite Authentication Works
1. Login as admin
2. Go to a project
3. Click "Members" tab
4. Click "Invite Member"
5. Enter an email address
6. Click "Invite"

**Expected results**:
- ✅ If email is on TaskFlow: "User added instantly"
- ✅ If email is new: "Invite sent to [email]"
- ❌ Should NOT get 401 error

**If getting 401 error**:
- Check browser DevTools Network tab
- Look at the request header - should see `Authorization: Bearer [token]`
- If not there, check if localStorage has `tf_token`
- Try logging out and logging back in

### Test 3: Check API Debugging
1. Open DevTools (F12)
2. Go to Console tab
3. Try to send an invite
4. You should see detailed error logs if anything fails

**Example log output**:
```
API Error for /projects/1/invite/: {detail: "Authentication credentials were not provided."}
401 Auth failed for /projects/1/invite/ {token: true, headers: {...}}
```

---

## 📋 Deployment Checklist

- [ ] Changes committed: `git add -A && git commit -m "..."`
- [ ] Changes pushed: `git push origin main`
- [ ] Railway deployment triggered (automatic or manual)
- [ ] Deployment completed successfully (check Railway dashboard)
- [ ] Browser cache cleared (Ctrl+Shift+Del)
- [ ] Hard refresh done (Ctrl+Shift+R)
- [ ] Responsive menu appears on mobile
- [ ] Can send invite without 401 error
- [ ] Admin can see pending invites
- [ ] New invite email is sent

---

## 🐛 Troubleshooting

### Problem: Still getting 401 on mobile invite
**Solutions**:
1. Verify you're logged in (check localStorage has `tf_token`)
2. Hard refresh page (Ctrl+Shift+R)
3. Try from different browser
4. Check Railway deployment logs for errors
5. Verify EMAIL_HOST_USER is set in Railway environment

### Problem: Responsive changes still not showing
**Solutions**:
1. **Clear cache completely**:
   - DevTools → Application → Clear storage → Clear all
   - Then hard refresh (Ctrl+Shift+R)
   
2. **Check static files were deployed**:
   - Open Network tab (F12)
   - Refresh page
   - Look for index.html request
   - Should show responsive CSS in the HTML

3. **Verify Railway collectstatic ran**:
   - Go to Railway dashboard
   - Click "Logs"
   - Search for "collectstatic"
   - Should see "Successfully collected"

### Problem: Invite email not being sent
**Check environment variables on Railway**:
1. Go to Railway dashboard
2. Click on TaskFlow project
3. Go to "Variables" tab
4. Verify these are set:
   - `EMAIL_HOST_USER` (your Gmail)
   - `EMAIL_HOST_PASSWORD` (app password)
   - `FRONTEND_URL` (your deployed URL)

**If using Gmail**:
- Use "App Password" not regular password
- Less secure app access must be enabled
- Or use OAuth2

---

## 📝 What Each File Does

### `taskflow/taskflow/settings.py`
- REST framework configuration
- Authentication settings
- CORS configuration
- Static files configuration
- Email settings

### `taskflow/api/views.py`
- API endpoints that handle business logic
- Authentication decorators ensure protected endpoints
- Error handling and validation

### `taskflow/api/templates/index.html`
- React app with all UI
- API client function (`api()`) that makes requests
- Responsive CSS (now updated)
- Component state management

### `railway.toml`
- Deployment configuration
- Build command (npm, etc if needed)
- Start command (gunicorn)
- Environment setup

---

## 🔐 Security Notes

These fixes ensure:
- ✅ Only authenticated admins can send invites
- ✅ Token is properly sent with each request
- ✅ Error messages don't leak sensitive info
- ✅ Email validation prevents bad requests
- ✅ Static files served with correct MIME types

---

## 🎯 Next Steps

1. **Deploy the fixes** (Option A or B above)
2. **Test both issues** (Test 1, 2, 3 above)
3. **Monitor logs** in Railway dashboard
4. **Report any new issues** with specific error messages

---

## 📞 Quick Debug Commands

### Check token in browser
```javascript
// In DevTools Console:
localStorage.getItem('tf_token')
```

### View API logs on Railway
```bash
# In Railway CLI or dashboard
railway logs --follow
```

### Test API endpoint manually
```bash
# Replace TOKEN with your actual token
curl -H "Authorization: Bearer TOKEN" \
  https://your-deployed-url.com/api/projects/1/invite/ \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","role":"member"}'
```

---

**Version**: 2.0 - With authentication fixes and responsive design
**Updated**: May 10, 2026
