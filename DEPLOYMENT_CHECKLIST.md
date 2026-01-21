# OTA Management - Deployment Checklist

Use this checklist before deploying to production.

## Pre-Build Checklist

### Code Quality
- [ ] All JavaScript files use `AppConfig.getAPIEndpoint()` for API calls
- [ ] No hardcoded URLs (http://localhost, 127.0.0.1)
- [ ] Frontend config.js properly detects Electron environment
- [ ] Socket.IO uses dynamic backend URL from config
- [ ] No console.error or console.log in production code (use debug mode)
- [ ] Error handling present for all API calls
- [ ] Network retry logic implemented for unreliable connections

### Backend Configuration
- [ ] Environment variables defined (DB_PATH, FIRMWARE_PATH, GW_IP, GW_TCP_PORT)
- [ ] Database paths point to user data directory
- [ ] TCP Gateway IP correct for your network
- [ ] Port 8000 available and not conflicting
- [ ] CORS settings appropriate for Electron
- [ ] Graceful shutdown handlers implemented
- [ ] Error messages user-friendly (no stack traces in UI)

### Electron Configuration
- [ ] Application icon created (icon.icns, icon.ico, icon.png)
- [ ] Icons in `assets/` directory
- [ ] Hardware acceleration disabled (no GPU console noise)
- [ ] User data directory properly initialized
- [ ] Menu shortcuts defined (Cmd+Shift+D for data folder)
- [ ] IPC bridge secure (preload.js)
- [ ] App name and version updated in package.json
- [ ] Build configuration in package.json correct for all platforms

### Dependencies
- [ ] All npm packages installed (`npm install`)
- [ ] Backend packages installed (`cd backend_nodejs && npm install`)
- [ ] No security vulnerabilities (`npm audit` passes)
- [ ] Package lock files committed to version control
- [ ] Version numbers frozen in package-lock.json (not "^" or "~")

### Database
- [ ] JSON schema verified (devices.json, software_list.json, softwares.json)
- [ ] Sample database files included for testing
- [ ] Database initialization works on fresh install
- [ ] Data directory creation permissions correct
- [ ] File encoding UTF-8 for all JSON files

### Documentation
- [ ] README.md updated with latest instructions
- [ ] PRODUCTION_SETUP.md reviewed and accurate
- [ ] USER_GUIDE.md complete with screenshots (if applicable)
- [ ] VERSION notes prepared
- [ ] Known issues documented

## Build Checklist

### Platform-Specific Requirements
#### macOS
- [ ] Xcode Command Line Tools installed (`xcode-select --install`)
- [ ] icon.icns file (512x512 or larger)
- [ ] Notarization key available (if signing required)
- [ ] Code signing certificate (if needed)

#### Windows
- [ ] Visual Studio Build Tools installed
- [ ] icon.ico file (256x256 or larger)
- [ ] .NET Framework available for installer

#### Linux
- [ ] GCC/G++ installed
- [ ] icon.png file (512x512 or larger)
- [ ] fakeroot package (for .deb creation)

### Build Process
- [ ] Run `npm install` (installs Electron & dependencies)
- [ ] Run `npm run build -- --mac` for macOS test
  - [ ] .dmg file generated in dist/
  - [ ] File size reasonable (>100 MB)
  - [ ] Notarization log checked (if applicable)
  
- [ ] Run `npm run build -- --win` for Windows test
  - [ ] .exe Setup file generated
  - [ ] Portable .exe also generated
  - [ ] File size reasonable (>150 MB)
  
- [ ] Run `npm run build -- --linux` for Linux test
  - [ ] .AppImage file generated
  - [ ] .deb package generated
  - [ ] File size reasonable (>150 MB)

- [ ] All dist/ outputs have proper naming:
  - macOS: `OTA Management-X.X.X-arm64.dmg` (Apple Silicon)
  - macOS: `OTA Management-X.X.X-x64.dmg` (Intel)
  - Windows: `OTA Management Setup X.X.X.exe`
  - Windows: `OTA Management X.X.X.exe` (portable)
  - Linux: `OTA Management-X.X.X.AppImage`
  - Linux: `OTA Management-X.X.X.deb`

## Testing Checklist

### Installation Testing
- [ ] macOS: Can install from .dmg (drag to Applications)
- [ ] macOS: App launches successfully
- [ ] Windows: Setup.exe installs without errors
- [ ] Windows: Add/Remove Programs shows app
- [ ] Windows: Uninstall works cleanly
- [ ] Linux AppImage: Executable without installation
- [ ] Linux Deb: `dpkg -i` and `apt remove` work

### Functional Testing
- [ ] Application window opens correctly
- [ ] All three tabs visible (Devices, Software, Tasks)
- [ ] Add Device feature works
- [ ] TCP Gateway connects automatically
- [ ] Add Software/upload firmware works
- [ ] Create task feature works
- [ ] WebSocket events update UI in real-time
- [ ] Menu options work (About, Logs, Open Data Folder)
- [ ] Keyboard shortcuts work (Cmd/Ctrl+Shift+D)

### Data Management Testing
- [ ] User data directory created at correct location:
  - [ ] macOS: ~/Library/Application Support/OTA Management/
  - [ ] Windows: %LOCALAPPDATA%\OTA Management\
  - [ ] Linux: ~/.config/OTA Management/
- [ ] Devices.json exists and is valid JSON
- [ ] Software_list.json exists and is valid JSON
- [ ] Tasks folder created
- [ ] "Open Data Folder" menu option opens file explorer
- [ ] Data persists between app restarts

### Network Testing
- [ ] Backend server starts automatically
- [ ] Backend listens on 127.0.0.1:8000
- [ ] TCP Gateway connects to 192.168.4.1:9001
- [ ] WebSocket connections established
- [ ] API endpoints respond correctly:
  - [ ] GET /api/devices
  - [ ] POST /api/devices
  - [ ] GET /api/software
  - [ ] POST /api/upload
  - [ ] GET /api/tasks
  - [ ] POST /api/tasks

### Performance Testing
- [ ] App launches in <5 seconds
- [ ] UI responsive with 10+ devices
- [ ] Memory usage <500 MB at rest
- [ ] No memory leaks (check after 1 hour use)
- [ ] CPU usage <10% at idle
- [ ] WebSocket handles 100+ messages/second

### Edge Case Testing
- [ ] Offline mode: Works when TCP Gateway unreachable
- [ ] Reconnection: Auto-reconnects when network returns
- [ ] Device removal: No crashes when device goes offline
- [ ] Large files: Handles 2+ MB firmware uploads
- [ ] Empty database: Works correctly on fresh install
- [ ] Corrupted data: Graceful error handling

## Security Checklist

### Data Security
- [ ] No credentials stored in code
- [ ] No sensitive data in logs
- [ ] Local-only communication (no cloud sync)
- [ ] User data directory properly isolated
- [ ] File permissions appropriate for OS

### Transport Security
- [ ] HTTP only (not HTTPS) for local development
- [ ] No self-signed cert warnings in logs
- [ ] WebSocket connections secured when needed
- [ ] CORS headers properly configured

### Code Security
- [ ] No `eval()` usage
- [ ] No insecure dependencies (`npm audit` clean)
- [ ] Input validation on all API endpoints
- [ ] SQL injection not applicable (JSON files)
- [ ] XSS prevention in frontend (no innerHTML)

## Release Checklist

### Version Management
- [ ] Version bumped in package.json (MAJOR.MINOR.PATCH)
- [ ] Version in electron/main.js matches
- [ ] Version in backend_nodejs/package.json matches
- [ ] CHANGELOG.md updated
- [ ] Git tags created: `v1.2.3`
- [ ] Release notes prepared

### Distribution Preparation
- [ ] All dist/ files properly named
- [ ] Checksum file generated (SHA256)
- [ ] README for release prepared
- [ ] Installation instructions validated
- [ ] Download links tested
- [ ] Virus scan performed (VirusTotal or similar)

### Documentation
- [ ] USER_GUIDE.md current
- [ ] PRODUCTION_SETUP.md current
- [ ] Troubleshooting section complete
- [ ] Screenshots current (if included)
- [ ] FAQ section prepared
- [ ] Support email/contact updated

### Publishing
- [ ] Files uploaded to distribution server
- [ ] Website updated with download links
- [ ] Announcement prepared
- [ ] Email notification to users (if applicable)
- [ ] Social media notification (if applicable)
- [ ] Support team notified

## Post-Release Checklist

### Monitoring
- [ ] Error logs monitored for 24 hours
- [ ] User feedback collected
- [ ] Performance metrics reviewed
- [ ] No critical bugs reported

### Support
- [ ] Support team trained on new version
- [ ] FAQ prepared based on early issues
- [ ] Known issues documented
- [ ] Rollback procedure tested

### Archive
- [ ] Release artifacts archived
- [ ] Source code tagged in Git
- [ ] Build logs archived
- [ ] Release notes saved
- [ ] User feedback documented

## Rollback Procedure (If Needed)

If critical issues found after release:

1. [ ] Identify issue from logs/user reports
2. [ ] Create hotfix branch: `git checkout -b hotfix/v1.2.4`
3. [ ] Fix issue in code
4. [ ] Test thoroughly
5. [ ] Build hotfix packages
6. [ ] Update version to X.X.(X+1)
7. [ ] Publish hotfix
8. [ ] Document issue and fix in release notes

## Sign-Off

- **Prepared By**: ____________________  Date: __________
- **Reviewed By**: ____________________  Date: __________
- **Approved By**: ____________________  Date: __________
- **Release Date**: __________

## Notes
```


```

---

**Remember**: This is a production application. Take time to test thoroughly. A solid release prevents user frustration and support burden.

