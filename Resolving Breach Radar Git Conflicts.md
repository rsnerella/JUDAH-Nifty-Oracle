# Chat Conversation

Note: _This is purely the output of the chat conversation and does not contain any raw data, codebase snippets, etc. used to generate the output._

### User Input

IN THE JUDAH PROJECT
2026-04-03T10:55:59.4385433Z Current runner version: '2.333.1'
2026-04-03T10:55:59.4409943Z ##[group]Runner Image Provisioner
2026-04-03T10:55:59.4410751Z Hosted Compute Agent
2026-04-03T10:55:59.4411247Z Version: 20260213.493
2026-04-03T10:55:59.4412411Z Commit: 5c115507f6dd24b8de37d8bbe0bb4509d0cc0fa3
2026-04-03T10:55:59.4413296Z Build Date: 2026-02-13T00:28:41Z
2026-04-03T10:55:59.4413893Z Worker ID: {d687a5b5-7208-43ba-a126-adff3dca2c22}
2026-04-03T10:55:59.4414650Z Azure Region: westus
2026-04-03T10:55:59.4415144Z ##[endgroup]
2026-04-03T10:55:59.4416813Z ##[group]Operating System
2026-04-03T10:55:59.4417814Z Ubuntu
2026-04-03T10:55:59.4418520Z 24.04.4
2026-04-03T10:55:59.4418960Z LTS
2026-04-03T10:55:59.4419477Z ##[endgroup]
2026-04-03T10:55:59.4419977Z ##[group]Runner Image
2026-04-03T10:55:59.4420491Z Image: ubuntu-24.04
2026-04-03T10:55:59.4421088Z Version: 20260329.72.1
2026-04-03T10:55:59.4422230Z Included Software: https://github.com/actions/runner-images/blob/ubuntu24/20260329.72/images/ubuntu/Ubuntu2404-Readme.md
2026-04-03T10:55:59.4423663Z Image Release: https://github.com/actions/runner-images/releases/tag/ubuntu24%2F20260329.72
2026-04-03T10:55:59.4424533Z ##[endgroup]
2026-04-03T10:55:59.4425563Z ##[group]GITHUB_TOKEN Permissions
2026-04-03T10:55:59.4427935Z Contents: write
2026-04-03T10:55:59.4428728Z Metadata: read
2026-04-03T10:55:59.4429355Z ##[endgroup]
2026-04-03T10:55:59.4431798Z Secret source: Actions
2026-04-03T10:55:59.4432501Z Prepare workflow directory
2026-04-03T10:55:59.4751431Z Prepare all required actions
2026-04-03T10:55:59.4788421Z Getting action download info
2026-04-03T10:55:59.9390533Z Download action repository 'actions/checkout@v4' (SHA:34e114876b0b11c390a56381ad16ebd13914f8d5)
2026-04-03T10:56:00.0964487Z Download action repository 'actions/setup-python@v5' (SHA:a26af69be951a213d495a4c3e4e4022e16d87065)
2026-04-03T10:56:00.2706966Z Complete job name: train-breach-models
2026-04-03T10:56:00.3391138Z ##[group]Run actions/checkout@v4
2026-04-03T10:56:00.3391951Z with:
2026-04-03T10:56:00.3392389Z   repository: pravindev666/JUDAH-Nifty-Oracle
2026-04-03T10:56:00.3393096Z   token: ***
2026-04-03T10:56:00.3393482Z   ssh-strict: true
2026-04-03T10:56:00.3393879Z   ssh-user: git
2026-04-03T10:56:00.3394285Z   persist-credentials: true
2026-04-03T10:56:00.3394735Z   clean: true
2026-04-03T10:56:00.3395131Z   sparse-checkout-cone-mode: true
2026-04-03T10:56:00.3395606Z   fetch-depth: 1
2026-04-03T10:56:00.3395990Z   fetch-tags: false
2026-04-03T10:56:00.3396602Z   show-progress: true
2026-04-03T10:56:00.3397018Z   lfs: false
2026-04-03T10:56:00.3397390Z   submodules: false
2026-04-03T10:56:00.3397799Z   set-safe-directory: true
2026-04-03T10:56:00.3398498Z ##[endgroup]
2026-04-03T10:56:00.4450922Z Syncing repository: pravindev666/JUDAH-Nifty-Oracle
2026-04-03T10:56:00.4452640Z ##[group]Getting Git version info
2026-04-03T10:56:00.4453538Z Working directory is '/home/runner/work/JUDAH-Nifty-Oracle/JUDAH-Nifty-Oracle'
2026-04-03T10:56:00.4454577Z [command]/usr/bin/git version
2026-04-03T10:56:00.4510021Z git version 2.53.0
2026-04-03T10:56:00.4535488Z ##[endgroup]
2026-04-03T10:56:00.4549532Z Temporarily overriding HOME='/home/runner/work/_temp/73402754-472f-4ffe-b373-ea3c155f8bb6' before making global git config changes
2026-04-03T10:56:00.4550863Z Adding repository directory to the temporary git global config as a safe directory
2026-04-03T10:56:00.4562507Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/JUDAH-Nifty-Oracle/JUDAH-Nifty-Oracle
2026-04-03T10:56:00.4592046Z Deleting the contents of '/home/runner/work/JUDAH-Nifty-Oracle/JUDAH-Nifty-Oracle'
2026-04-03T10:56:00.4595322Z ##[group]Initializing the repository
2026-04-03T10:56:00.4599801Z [command]/usr/bin/git init /home/runner/work/JUDAH-Nifty-Oracle/JUDAH-Nifty-Oracle
2026-04-03T10:56:00.4696664Z hint: Using 'master' as the name for the initial branch. This default branch name
2026-04-03T10:56:00.4698407Z hint: will change to "main" in Git 3.0. To configure the initial branch name
2026-04-03T10:56:00.4699961Z hint: to use in all of your new repositories, which will suppress this warning,
2026-04-03T10:56:00.4701621Z hint: call:
2026-04-03T10:56:00.4702280Z hint:
2026-04-03T10:56:00.4703304Z hint: 	git config --global init.defaultBranch <name>
2026-04-03T10:56:00.4704391Z hint:
2026-04-03T10:56:00.4705368Z hint: Names commonly chosen instead of 'master' are 'main', 'trunk' and
2026-04-03T10:56:00.4707189Z hint: 'development'. The just-created branch can be renamed via this command:
2026-04-03T10:56:00.4708451Z hint:
2026-04-03T10:56:00.4709158Z hint: 	git branch -m <name>
2026-04-03T10:56:00.4709933Z hint:
2026-04-03T10:56:00.4711009Z hint: Disable this message with "git config set advice.defaultBranchName false"
2026-04-03T10:56:00.4712945Z Initialized empty Git repository in /home/runner/work/JUDAH-Nifty-Oracle/JUDAH-Nifty-Oracle/.git/
2026-04-03T10:56:00.4715829Z [command]/usr/bin/git remote add origin https://github.com/pravindev666/JUDAH-Nifty-Oracle
2026-04-03T10:56:00.4742215Z ##[endgroup]
2026-04-03T10:56:00.4743428Z ##[group]Disabling automatic garbage collection
2026-04-03T10:56:00.4746174Z [command]/usr/bin/git config --local gc.auto 0
2026-04-03T10:56:00.4774638Z ##[endgroup]
2026-04-03T10:56:00.4775880Z ##[group]Setting up auth
2026-04-03T10:56:00.4781736Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-04-03T10:56:00.4811546Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-04-03T10:56:00.5149891Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-04-03T10:56:00.5181547Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-04-03T10:56:00.5413492Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-04-03T10:56:00.5456683Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-04-03T10:56:00.5686131Z [command]/usr/bin/git config --local http.https://github.com/.extraheader AUTHORIZATION: basic ***
2026-04-03T10:56:00.5719255Z ##[endgroup]
2026-04-03T10:56:00.5720476Z ##[group]Fetching the repository
2026-04-03T10:56:00.5728491Z [command]/usr/bin/git -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +321adee99bd547b8e01ff40f43c52ef3eaa48d0b:refs/remotes/origin/main
2026-04-03T10:56:03.8601004Z From https://github.com/pravindev666/JUDAH-Nifty-Oracle
2026-04-03T10:56:03.8602841Z  * [new ref]         321adee99bd547b8e01ff40f43c52ef3eaa48d0b -> origin/main
2026-04-03T10:56:03.8630561Z ##[endgroup]
2026-04-03T10:56:03.8631937Z ##[group]Determining the checkout info
2026-04-03T10:56:03.8633903Z ##[endgroup]
2026-04-03T10:56:03.8638504Z [command]/usr/bin/git sparse-checkout disable
2026-04-03T10:56:03.8676862Z [command]/usr/bin/git config --local --unset-all extensions.worktreeConfig
2026-04-03T10:56:03.8702826Z ##[group]Checking out the ref
2026-04-03T10:56:03.8707509Z [command]/usr/bin/git checkout --progress --force -B main refs/remotes/origin/main
2026-04-03T10:56:03.9648706Z Switched to a new branch 'main'
2026-04-03T10:56:03.9650463Z branch 'main' set up to track 'origin/main'.
2026-04-03T10:56:03.9662568Z ##[endgroup]
2026-04-03T10:56:03.9698061Z [command]/usr/bin/git log -1 --format=%H
2026-04-03T10:56:03.9719702Z 321adee99bd547b8e01ff40f43c52ef3eaa48d0b
2026-04-03T10:56:04.0034460Z ##[group]Run actions/setup-python@v5
2026-04-03T10:56:04.0035676Z with:
2026-04-03T10:56:04.0036674Z   python-version: 3.12
2026-04-03T10:56:04.0037644Z   cache: pip
2026-04-03T10:56:04.0038494Z   check-latest: false
2026-04-03T10:56:04.0039703Z   token: ***
2026-04-03T10:56:04.0040598Z   update-environment: true
2026-04-03T10:56:04.0041656Z   allow-prereleases: false
2026-04-03T10:56:04.0042696Z   freethreaded: false
2026-04-03T10:56:04.0043816Z ##[endgroup]
2026-04-03T10:56:04.1676607Z ##[group]Installed versions
2026-04-03T10:56:04.1781636Z Successfully set up CPython (3.12.13)
2026-04-03T10:56:04.1783477Z ##[endgroup]
2026-04-03T10:56:04.2561166Z [command]/opt/hostedtoolcache/Python/3.12.13/x64/bin/pip cache dir
2026-04-03T10:56:06.3102541Z /home/runner/.cache/pip
2026-04-03T10:56:06.5972463Z Cache hit for: setup-python-Linux-x64-24.04-Ubuntu-python-3.12.13-pip-8ed6bb37dec893fa8fe94d6dfbe1ca53cb20faecc9f6a3cb825a657c972bc17f
2026-04-03T10:56:07.8820656Z Received 4194304 of 611960708 (0.7%), 4.0 MBs/sec
2026-04-03T10:56:08.8831327Z Received 125829120 of 611960708 (20.6%), 59.9 MBs/sec
2026-04-03T10:56:09.8833658Z Received 255852544 of 611960708 (41.8%), 81.3 MBs/sec
2026-04-03T10:56:10.8873417Z Received 402653184 of 611960708 (65.8%), 95.8 MBs/sec
2026-04-03T10:56:11.8875697Z Received 583008256 of 611960708 (95.3%), 111.0 MBs/sec
2026-04-03T10:56:12.1095306Z Received 611960708 of 611960708 (100.0%), 111.6 MBs/sec
2026-04-03T10:56:12.1097165Z Cache Size: ~584 MB (611960708 B)
2026-04-03T10:56:12.1226793Z [command]/usr/bin/tar -xf /home/runner/work/_temp/282c1c8f-d39d-4f8a-a635-b563f468944e/cache.tzst -P -C /home/runner/work/JUDAH-Nifty-Oracle/JUDAH-Nifty-Oracle --use-compress-program unzstd
2026-04-03T10:56:12.8699106Z Cache restored successfully
2026-04-03T10:56:12.8959482Z Cache restored from key: setup-python-Linux-x64-24.04-Ubuntu-python-3.12.13-pip-8ed6bb37dec893fa8fe94d6dfbe1ca53cb20faecc9f6a3cb825a657c972bc17f
2026-04-03T10:56:12.9122334Z ##[group]Run pip install -r requirements.txt
2026-04-03T10:56:12.9122745Z [36;1mpip install -r requirements.txt[0m
2026-04-03T10:56:12.9155473Z shell: /usr/bin/bash -e {0}
2026-04-03T10:56:12.9155759Z env:
2026-04-03T10:56:12.9156015Z   pythonLocation: /opt/hostedtoolcache/Python/3.12.13/x64
2026-04-03T10:56:12.9156762Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.12.13/x64/lib/pkgconfig
2026-04-03T10:56:12.9157194Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.13/x64
2026-04-03T10:56:12.9157579Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.13/x64
2026-04-03T10:56:12.9157938Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.13/x64
2026-04-03T10:56:12.9158303Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.12.13/x64/lib
2026-04-03T10:56:12.9158604Z ##[endgroup]
2026-04-03T10:56:14.4874585Z Collecting streamlit>=1.32.0 (from -r requirements.txt (line 1))
2026-04-03T10:56:14.5475416Z   Downloading streamlit-1.56.0-py3-none-any.whl.metadata (9.8 kB)
2026-04-03T10:56:14.6741967Z Collecting pandas>=2.0.0 (from -r requirements.txt (line 2))
2026-04-03T10:56:14.6771036Z   Downloading pandas-3.0.2-cp312-cp312-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl.metadata (79 kB)
2026-04-03T10:56:14.8900231Z Collecting numpy>=1.24.0 (from -r requirements.txt (line 3))
2026-04-03T10:56:14.8913480Z   Using cached numpy-2.4.4-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl.metadata (6.6 kB)
2026-04-03T10:56:14.9996759Z Collecting scipy>=1.10.0 (from -r requirements.txt (line 4))
2026-04-03T10:56:15.0009622Z   Using cached scipy-1.17.1-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl.metadata (62 kB)
2026-04-03T10:56:15.0389193Z Collecting plotly>=5.18.0 (from -r requirements.txt (line 5))
2026-04-03T10:56:15.0400726Z   Using cached plotly-6.6.0-py3-none-any.whl.metadata (8.5 kB)
2026-04-03T10:56:15.0615669Z Collecting yfinance>=0.2.36 (from -r requirements.txt (line 6))
2026-04-03T10:56:15.0626877Z   Using cached yfinance-1.2.0-py2.py3-none-any.whl.metadata (6.1 kB)
2026-04-03T10:56:15.0813427Z Collecting requests>=2.28.0 (from -r requirements.txt (line 7))
2026-04-03T10:56:15.0837604Z   Downloading requests-2.33.1-py3-none-any.whl.metadata (4.8 kB)
2026-04-03T10:56:15.1571115Z Collecting scikit-learn>=1.3.0 (from -r requirements.txt (line 8))
2026-04-03T10:56:15.1582810Z   Using cached scikit_learn-1.8.0-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl.metadata (11 kB)
2026-04-03T10:56:15.1874912Z Collecting xgboost>=2.0.0 (from -r requirements.txt (line 9))
2026-04-03T10:56:15.1886382Z   Using cached xgboost-3.2.0-py3-none-manylinux_2_28_x86_64.whl.metadata (2.1 kB)
2026-04-03T10:56:15.2034653Z Collecting joblib>=1.3.0 (from -r requirements.txt (line 10))
2026-04-03T10:56:15.2045978Z   Using cached joblib-1.5.3-py3-none-any.whl.metadata (5.5 kB)
2026-04-03T10:56:15.3555213Z Collecting matplotlib>=3.7.0 (from -r requirements.txt (line 11))
2026-04-03T10:56:15.3572552Z   Using cached matplotlib-3.10.8-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (52 kB)
2026-04-03T10:56:15.6959641Z Collecting altair!=5.4.0,!=5.4.1,<7,>=4.0 (from streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:15.6971221Z   Using cached altair-6.0.0-py3-none-any.whl.metadata (11 kB)
2026-04-03T10:56:15.7094248Z Collecting blinker<2,>=1.5.0 (from streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:15.7105108Z   Using cached blinker-1.9.0-py3-none-any.whl.metadata (1.6 kB)
2026-04-03T10:56:15.7222894Z Collecting cachetools<8,>=5.5 (from streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:15.7234197Z   Using cached cachetools-7.0.5-py3-none-any.whl.metadata (5.6 kB)
2026-04-03T10:56:15.7353279Z Collecting click<9,>=7.0 (from streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:15.7364188Z   Using cached click-8.3.1-py3-none-any.whl.metadata (2.6 kB)
2026-04-03T10:56:15.7528203Z Collecting gitpython!=3.1.19,<4,>=3.0.7 (from streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:15.7539396Z   Using cached gitpython-3.1.46-py3-none-any.whl.metadata (13 kB)
2026-04-03T10:56:15.7701057Z Collecting packaging>=20 (from streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:15.7712080Z   Using cached packaging-26.0-py3-none-any.whl.metadata (3.3 kB)
2026-04-03T10:56:15.9284572Z Collecting pillow<13,>=7.1.0 (from streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:15.9313255Z   Downloading pillow-12.2.0-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl.metadata (8.8 kB)
2026-04-03T10:56:15.9469571Z Collecting pydeck<1,>=0.8.0b4 (from streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:15.9480738Z   Using cached pydeck-0.9.1-py2.py3-none-any.whl.metadata (4.1 kB)
2026-04-03T10:56:16.0877881Z Collecting protobuf<8,>=3.20 (from streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:16.0902679Z   Downloading protobuf-7.34.1-cp310-abi3-manylinux2014_x86_64.whl.metadata (595 bytes)
2026-04-03T10:56:16.1628083Z Collecting pyarrow>=7.0 (from streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:16.1639880Z   Using cached pyarrow-23.0.1-cp312-cp312-manylinux_2_28_x86_64.whl.metadata (3.1 kB)
2026-04-03T10:56:16.1771260Z Collecting tenacity<10,>=8.1.0 (from streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:16.1782233Z   Using cached tenacity-9.1.4-py3-none-any.whl.metadata (1.2 kB)
2026-04-03T10:56:16.1858128Z Collecting toml<2,>=0.10.1 (from streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:16.1869106Z   Using cached toml-0.10.2-py2.py3-none-any.whl.metadata (7.1 kB)
2026-04-03T10:56:16.2163603Z Collecting tornado!=6.5.0,<7,>=6.0.3 (from streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:16.2175182Z   Using cached tornado-6.5.5-cp39-abi3-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl.metadata (2.8 kB)
2026-04-03T10:56:16.2286717Z Collecting typing-extensions<5,>=4.10.0 (from streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:16.2298617Z   Using cached typing_extensions-4.15.0-py3-none-any.whl.metadata (3.3 kB)
2026-04-03T10:56:16.2672023Z Collecting watchdog<7,>=2.1.5 (from streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:16.2684137Z   Using cached watchdog-6.0.0-py3-none-manylinux2014_x86_64.whl.metadata (44 kB)
2026-04-03T10:56:16.2833129Z Collecting python-dateutil>=2.8.2 (from pandas>=2.0.0->-r requirements.txt (line 2))
2026-04-03T10:56:16.2844393Z   Using cached python_dateutil-2.9.0.post0-py2.py3-none-any.whl.metadata (8.4 kB)
2026-04-03T10:56:16.4088158Z Collecting charset_normalizer<4,>=2 (from requests>=2.28.0->-r requirements.txt (line 7))
2026-04-03T10:56:16.4115580Z   Downloading charset_normalizer-3.4.7-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (40 kB)
2026-04-03T10:56:16.4261105Z Collecting idna<4,>=2.5 (from requests>=2.28.0->-r requirements.txt (line 7))
2026-04-03T10:56:16.4272362Z   Using cached idna-3.11-py3-none-any.whl.metadata (8.4 kB)
2026-04-03T10:56:16.4445999Z Collecting urllib3<3,>=1.26 (from requests>=2.28.0->-r requirements.txt (line 7))
2026-04-03T10:56:16.4457049Z   Using cached urllib3-2.6.3-py3-none-any.whl.metadata (6.9 kB)
2026-04-03T10:56:16.4605678Z Collecting certifi>=2023.5.7 (from requests>=2.28.0->-r requirements.txt (line 7))
2026-04-03T10:56:16.4616768Z   Using cached certifi-2026.2.25-py3-none-any.whl.metadata (2.5 kB)
2026-04-03T10:56:16.4732686Z Collecting jinja2 (from altair!=5.4.0,!=5.4.1,<7,>=4.0->streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:16.4743501Z   Using cached jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
2026-04-03T10:56:16.4922253Z Collecting jsonschema>=3.0 (from altair!=5.4.0,!=5.4.1,<7,>=4.0->streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:16.4933029Z   Using cached jsonschema-4.26.0-py3-none-any.whl.metadata (7.6 kB)
2026-04-03T10:56:16.5235616Z Collecting narwhals>=1.27.1 (from altair!=5.4.0,!=5.4.1,<7,>=4.0->streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:16.5247392Z   Using cached narwhals-2.18.1-py3-none-any.whl.metadata (14 kB)
2026-04-03T10:56:16.5416264Z Collecting gitdb<5,>=4.0.1 (from gitpython!=3.1.19,<4,>=3.0.7->streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:16.5427351Z   Using cached gitdb-4.0.12-py3-none-any.whl.metadata (1.2 kB)
2026-04-03T10:56:16.5507386Z Collecting smmap<6,>=3.0.1 (from gitdb<5,>=4.0.1->gitpython!=3.1.19,<4,>=3.0.7->streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:16.5518397Z   Using cached smmap-5.0.3-py3-none-any.whl.metadata (4.6 kB)
2026-04-03T10:56:16.5842998Z Collecting multitasking>=0.0.7 (from yfinance>=0.2.36->-r requirements.txt (line 6))
2026-04-03T10:56:16.5844218Z   Using cached multitasking-0.0.12-py3-none-any.whl
2026-04-03T10:56:16.6040256Z Collecting platformdirs>=2.0.0 (from yfinance>=0.2.36->-r requirements.txt (line 6))
2026-04-03T10:56:16.6051366Z   Using cached platformdirs-4.9.4-py3-none-any.whl.metadata (4.7 kB)
2026-04-03T10:56:16.6330956Z Collecting pytz>=2022.5 (from yfinance>=0.2.36->-r requirements.txt (line 6))
2026-04-03T10:56:16.6342132Z   Using cached pytz-2026.1.post1-py2.py3-none-any.whl.metadata (22 kB)
2026-04-03T10:56:16.6701802Z Collecting frozendict>=2.3.4 (from yfinance>=0.2.36->-r requirements.txt (line 6))
2026-04-03T10:56:16.6712689Z   Using cached frozendict-2.4.7-py3-none-any.whl.metadata (23 kB)
2026-04-03T10:56:16.6865661Z Collecting peewee>=3.16.2 (from yfinance>=0.2.36->-r requirements.txt (line 6))
2026-04-03T10:56:16.6887993Z   Downloading peewee-4.0.4-py3-none-any.whl.metadata (8.6 kB)
2026-04-03T10:56:16.7032957Z Collecting beautifulsoup4>=4.11.1 (from yfinance>=0.2.36->-r requirements.txt (line 6))
2026-04-03T10:56:16.7043939Z   Using cached beautifulsoup4-4.14.3-py3-none-any.whl.metadata (3.8 kB)
2026-04-03T10:56:16.7513969Z Collecting curl_cffi<0.14,>=0.7 (from yfinance>=0.2.36->-r requirements.txt (line 6))
2026-04-03T10:56:16.7525549Z   Using cached curl_cffi-0.13.0-cp39-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (13 kB)
2026-04-03T10:56:16.8409742Z Collecting websockets>=13.0 (from yfinance>=0.2.36->-r requirements.txt (line 6))
2026-04-03T10:56:16.8421795Z   Using cached websockets-16.0-cp312-cp312-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl.metadata (6.8 kB)
2026-04-03T10:56:16.9297143Z Collecting cffi>=1.12.0 (from curl_cffi<0.14,>=0.7->yfinance>=0.2.36->-r requirements.txt (line 6))
2026-04-03T10:56:16.9308947Z   Using cached cffi-2.0.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (2.6 kB)
2026-04-03T10:56:16.9432144Z Collecting threadpoolctl>=3.2.0 (from scikit-learn>=1.3.0->-r requirements.txt (line 8))
2026-04-03T10:56:16.9443048Z   Using cached threadpoolctl-3.6.0-py3-none-any.whl.metadata (13 kB)
2026-04-03T10:56:16.9550461Z Collecting nvidia-nccl-cu12 (from xgboost>=2.0.0->-r requirements.txt (line 9))
2026-04-03T10:56:16.9561482Z   Using cached nvidia_nccl_cu12-2.29.7-py3-none-manylinux_2_18_x86_64.whl.metadata (2.1 kB)
2026-04-03T10:56:17.0109203Z Collecting contourpy>=1.0.1 (from matplotlib>=3.7.0->-r requirements.txt (line 11))
2026-04-03T10:56:17.0120853Z   Using cached contourpy-1.3.3-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl.metadata (5.5 kB)
2026-04-03T10:56:17.0200969Z Collecting cycler>=0.10 (from matplotlib>=3.7.0->-r requirements.txt (line 11))
2026-04-03T10:56:17.0212247Z   Using cached cycler-0.12.1-py3-none-any.whl.metadata (3.8 kB)
2026-04-03T10:56:17.2038539Z Collecting fonttools>=4.22.0 (from matplotlib>=3.7.0->-r requirements.txt (line 11))
2026-04-03T10:56:17.2051783Z   Using cached fonttools-4.62.1-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (117 kB)
2026-04-03T10:56:17.2690615Z Collecting kiwisolver>=1.3.1 (from matplotlib>=3.7.0->-r requirements.txt (line 11))
2026-04-03T10:56:17.2702672Z   Using cached kiwisolver-1.5.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (5.1 kB)
2026-04-03T10:56:17.2911840Z Collecting pyparsing>=3 (from matplotlib>=3.7.0->-r requirements.txt (line 11))
2026-04-03T10:56:17.2923520Z   Using cached pyparsing-3.3.2-py3-none-any.whl.metadata (5.8 kB)
2026-04-03T10:56:17.3061268Z Collecting soupsieve>=1.6.1 (from beautifulsoup4>=4.11.1->yfinance>=0.2.36->-r requirements.txt (line 6))
2026-04-03T10:56:17.3071901Z   Using cached soupsieve-2.8.3-py3-none-any.whl.metadata (4.6 kB)
2026-04-03T10:56:17.3166992Z Collecting pycparser (from cffi>=1.12.0->curl_cffi<0.14,>=0.7->yfinance>=0.2.36->-r requirements.txt (line 6))
2026-04-03T10:56:17.3178179Z   Using cached pycparser-3.0-py3-none-any.whl.metadata (8.2 kB)
2026-04-03T10:56:17.3751484Z Collecting MarkupSafe>=2.0 (from jinja2->altair!=5.4.0,!=5.4.1,<7,>=4.0->streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:17.3763631Z   Using cached markupsafe-3.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (2.7 kB)
2026-04-03T10:56:17.3865324Z Collecting attrs>=22.2.0 (from jsonschema>=3.0->altair!=5.4.0,!=5.4.1,<7,>=4.0->streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:17.3876037Z   Using cached attrs-26.1.0-py3-none-any.whl.metadata (8.8 kB)
2026-04-03T10:56:17.3964338Z Collecting jsonschema-specifications>=2023.03.6 (from jsonschema>=3.0->altair!=5.4.0,!=5.4.1,<7,>=4.0->streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:17.3975108Z   Using cached jsonschema_specifications-2025.9.1-py3-none-any.whl.metadata (2.9 kB)
2026-04-03T10:56:17.4146841Z Collecting referencing>=0.28.4 (from jsonschema>=3.0->altair!=5.4.0,!=5.4.1,<7,>=4.0->streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:17.4157883Z   Using cached referencing-0.37.0-py3-none-any.whl.metadata (2.8 kB)
2026-04-03T10:56:17.6520719Z Collecting rpds-py>=0.25.0 (from jsonschema>=3.0->altair!=5.4.0,!=5.4.1,<7,>=4.0->streamlit>=1.32.0->-r requirements.txt (line 1))
2026-04-03T10:56:17.6534279Z   Using cached rpds_py-0.30.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (4.1 kB)
2026-04-03T10:56:17.6711625Z Collecting six>=1.5 (from python-dateutil>=2.8.2->pandas>=2.0.0->-r requirements.txt (line 2))
2026-04-03T10:56:17.6722806Z   Using cached six-1.17.0-py2.py3-none-any.whl.metadata (1.7 kB)
2026-04-03T10:56:17.6848853Z Downloading streamlit-1.56.0-py3-none-any.whl (9.1 MB)
2026-04-03T10:56:17.7287923Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 9.1/9.1 MB 232.0 MB/s  0:00:00
2026-04-03T10:56:17.7314075Z Downloading pandas-3.0.2-cp312-cp312-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl (10.9 MB)
2026-04-03T10:56:17.7626391Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 10.9/10.9 MB 365.8 MB/s  0:00:00
2026-04-03T10:56:17.7639058Z Using cached numpy-2.4.4-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl (16.6 MB)
2026-04-03T10:56:17.7721255Z Downloading requests-2.33.1-py3-none-any.whl (64 kB)
2026-04-03T10:56:17.7755035Z Using cached altair-6.0.0-py3-none-any.whl (795 kB)
2026-04-03T10:56:17.7769019Z Using cached blinker-1.9.0-py3-none-any.whl (8.5 kB)
2026-04-03T10:56:17.7781169Z Using cached cachetools-7.0.5-py3-none-any.whl (13 kB)
2026-04-03T10:56:17.7807476Z Downloading charset_normalizer-3.4.7-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (216 kB)
2026-04-03T10:56:17.7844463Z Using cached click-8.3.1-py3-none-any.whl (108 kB)
2026-04-03T10:56:17.7856049Z Using cached gitpython-3.1.46-py3-none-any.whl (208 kB)
2026-04-03T10:56:17.7868100Z Using cached gitdb-4.0.12-py3-none-any.whl (62 kB)
2026-04-03T10:56:17.7879659Z Using cached idna-3.11-py3-none-any.whl (71 kB)
2026-04-03T10:56:17.7906707Z Downloading pillow-12.2.0-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl (7.1 MB)
2026-04-03T10:56:17.8124254Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 7.1/7.1 MB 349.5 MB/s  0:00:00
2026-04-03T10:56:17.8152264Z Downloading protobuf-7.34.1-cp310-abi3-manylinux2014_x86_64.whl (324 kB)
2026-04-03T10:56:17.8190318Z Using cached pydeck-0.9.1-py2.py3-none-any.whl (6.9 MB)
2026-04-03T10:56:17.8224632Z Using cached smmap-5.0.3-py3-none-any.whl (24 kB)
2026-04-03T10:56:17.8235438Z Using cached tenacity-9.1.4-py3-none-any.whl (28 kB)
2026-04-03T10:56:17.8246772Z Using cached toml-0.10.2-py2.py3-none-any.whl (16 kB)
2026-04-03T10:56:17.8258396Z Using cached tornado-6.5.5-cp39-abi3-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (447 kB)
2026-04-03T10:56:17.8270579Z Using cached typing_extensions-4.15.0-py3-none-any.whl (44 kB)
2026-04-03T10:56:17.8281488Z Using cached urllib3-2.6.3-py3-none-any.whl (131 kB)
2026-04-03T10:56:17.8292659Z Using cached watchdog-6.0.0-py3-none-manylinux2014_x86_64.whl (79 kB)
2026-04-03T10:56:17.8303928Z Using cached scipy-1.17.1-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl (35.2 MB)
2026-04-03T10:56:17.8443872Z Using cached plotly-6.6.0-py3-none-any.whl (9.9 MB)
2026-04-03T10:56:17.8489362Z Using cached yfinance-1.2.0-py2.py3-none-any.whl (130 kB)
2026-04-03T10:56:17.8500900Z Using cached curl_cffi-0.13.0-cp39-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (8.3 MB)
2026-04-03T10:56:17.8540442Z Using cached scikit_learn-1.8.0-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl (8.9 MB)
2026-04-03T10:56:17.8583690Z Using cached xgboost-3.2.0-py3-none-manylinux_2_28_x86_64.whl (131.7 MB)
2026-04-03T10:56:17.9045684Z Using cached joblib-1.5.3-py3-none-any.whl (309 kB)
2026-04-03T10:56:17.9058125Z Using cached matplotlib-3.10.8-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (8.7 MB)
2026-04-03T10:56:17.9098727Z Using cached beautifulsoup4-4.14.3-py3-none-any.whl (107 kB)
2026-04-03T10:56:17.9109822Z Using cached certifi-2026.2.25-py3-none-any.whl (153 kB)
2026-04-03T10:56:17.9121426Z Using cached cffi-2.0.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (219 kB)
2026-04-03T10:56:17.9132953Z Using cached contourpy-1.3.3-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl (362 kB)
2026-04-03T10:56:17.9145590Z Using cached cycler-0.12.1-py3-none-any.whl (8.3 kB)
2026-04-03T10:56:17.9156851Z Using cached fonttools-4.62.1-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (5.0 MB)
2026-04-03T10:56:17.9184893Z Using cached frozendict-2.4.7-py3-none-any.whl (16 kB)
2026-04-03T10:56:17.9195529Z Using cached jinja2-3.1.6-py3-none-any.whl (134 kB)
2026-04-03T10:56:17.9206935Z Using cached jsonschema-4.26.0-py3-none-any.whl (90 kB)
2026-04-03T10:56:17.9217961Z Using cached attrs-26.1.0-py3-none-any.whl (67 kB)
2026-04-03T10:56:17.9229118Z Using cached jsonschema_specifications-2025.9.1-py3-none-any.whl (18 kB)
2026-04-03T10:56:17.9240082Z Using cached kiwisolver-1.5.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (1.5 MB)
2026-04-03T10:56:17.9256233Z Using cached markupsafe-3.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (22 kB)
2026-04-03T10:56:17.9266760Z Using cached narwhals-2.18.1-py3-none-any.whl (444 kB)
2026-04-03T10:56:17.9279232Z Using cached packaging-26.0-py3-none-any.whl (74 kB)
2026-04-03T10:56:17.9304418Z Downloading peewee-4.0.4-py3-none-any.whl (144 kB)
2026-04-03T10:56:17.9341327Z Using cached platformdirs-4.9.4-py3-none-any.whl (21 kB)
2026-04-03T10:56:17.9352819Z Using cached pyarrow-23.0.1-cp312-cp312-manylinux_2_28_x86_64.whl (47.6 MB)
2026-04-03T10:56:17.9529334Z Using cached pyparsing-3.3.2-py3-none-any.whl (122 kB)
2026-04-03T10:56:17.9540939Z Using cached python_dateutil-2.9.0.post0-py2.py3-none-any.whl (229 kB)
2026-04-03T10:56:17.9552979Z Using cached pytz-2026.1.post1-py2.py3-none-any.whl (510 kB)
2026-04-03T10:56:17.9565550Z Using cached referencing-0.37.0-py3-none-any.whl (26 kB)
2026-04-03T10:56:17.9576698Z Using cached rpds_py-0.30.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (394 kB)
2026-04-03T10:56:17.9588891Z Using cached six-1.17.0-py2.py3-none-any.whl (11 kB)
2026-04-03T10:56:17.9599684Z Using cached soupsieve-2.8.3-py3-none-any.whl (37 kB)
2026-04-03T10:56:17.9610504Z Using cached threadpoolctl-3.6.0-py3-none-any.whl (18 kB)
2026-04-03T10:56:17.9621646Z Using cached websockets-16.0-cp312-cp312-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (184 kB)
2026-04-03T10:56:17.9632985Z Using cached nvidia_nccl_cu12-2.29.7-py3-none-manylinux_2_18_x86_64.whl (293.6 MB)
2026-04-03T10:56:18.0641206Z Using cached pycparser-3.0-py3-none-any.whl (48 kB)
2026-04-03T10:56:18.7335695Z Installing collected packages: pytz, peewee, multitasking, websockets, watchdog, urllib3, typing-extensions, tornado, toml, threadpoolctl, tenacity, soupsieve, smmap, six, rpds-py, pyparsing, pycparser, pyarrow, protobuf, platformdirs, pillow, packaging, nvidia-nccl-cu12, numpy, narwhals, MarkupSafe, kiwisolver, joblib, idna, frozendict, fonttools, cycler, click, charset_normalizer, certifi, cachetools, blinker, attrs, scipy, requests, referencing, python-dateutil, plotly, jinja2, gitdb, contourpy, cffi, beautifulsoup4, xgboost, scikit-learn, pydeck, pandas, matplotlib, jsonschema-specifications, gitpython, curl_cffi, yfinance, jsonschema, altair, streamlit
2026-04-03T10:56:45.4728430Z 
2026-04-03T10:56:45.4781721Z Successfully installed MarkupSafe-3.0.3 altair-6.0.0 attrs-26.1.0 beautifulsoup4-4.14.3 blinker-1.9.0 cachetools-7.0.5 certifi-2026.2.25 cffi-2.0.0 charset_normalizer-3.4.7 click-8.3.1 contourpy-1.3.3 curl_cffi-0.13.0 cycler-0.12.1 fonttools-4.62.1 frozendict-2.4.7 gitdb-4.0.12 gitpython-3.1.46 idna-3.11 jinja2-3.1.6 joblib-1.5.3 jsonschema-4.26.0 jsonschema-specifications-2025.9.1 kiwisolver-1.5.0 matplotlib-3.10.8 multitasking-0.0.12 narwhals-2.18.1 numpy-2.4.4 nvidia-nccl-cu12-2.29.7 packaging-26.0 pandas-3.0.2 peewee-4.0.4 pillow-12.2.0 platformdirs-4.9.4 plotly-6.6.0 protobuf-7.34.1 pyarrow-23.0.1 pycparser-3.0 pydeck-0.9.1 pyparsing-3.3.2 python-dateutil-2.9.0.post0 pytz-2026.1.post1 referencing-0.37.0 requests-2.33.1 rpds-py-0.30.0 scikit-learn-1.8.0 scipy-1.17.1 six-1.17.0 smmap-5.0.3 soupsieve-2.8.3 streamlit-1.56.0 tenacity-9.1.4 threadpoolctl-3.6.0 toml-0.10.2 tornado-6.5.5 typing-extensions-4.15.0 urllib3-2.6.3 watchdog-6.0.0 websockets-16.0 xgboost-3.2.0 yfinance-1.2.0
2026-04-03T10:56:45.8739708Z ##[group]Run python -m engine.breach_trainer
2026-04-03T10:56:45.8740044Z [36;1mpython -m engine.breach_trainer[0m
2026-04-03T10:56:45.8768112Z shell: /usr/bin/bash -e {0}
2026-04-03T10:56:45.8768344Z env:
2026-04-03T10:56:45.8768587Z   pythonLocation: /opt/hostedtoolcache/Python/3.12.13/x64
2026-04-03T10:56:45.8769009Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.12.13/x64/lib/pkgconfig
2026-04-03T10:56:45.8769418Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.13/x64
2026-04-03T10:56:45.8769788Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.13/x64
2026-04-03T10:56:45.8770150Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.13/x64
2026-04-03T10:56:45.8770508Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.12.13/x64/lib
2026-04-03T10:56:45.8771007Z   PYTHONUNBUFFERED: 1
2026-04-03T10:56:45.8771214Z   PYTHONIOENCODING: utf-8
2026-04-03T10:56:45.8771411Z ##[endgroup]
2026-04-03T10:56:49.3362639Z 🛡️ BREACH RADAR — Credit Spread Safety Trainer
2026-04-03T10:56:49.3363465Z ============================================================
2026-04-03T10:56:49.3364087Z Threshold: ±2.5% (~600 pts)
2026-04-03T10:56:49.3364496Z Horizons: [3, 5, 7, 14, 21, 30]
2026-04-03T10:56:49.3364934Z ============================================================
2026-04-03T10:56:49.3365288Z 
2026-04-03T10:56:49.3365495Z 📦 Building features...
2026-04-03T10:56:52.3411522Z ✅ 2730 rows, 274 columns loaded.
2026-04-03T10:56:52.3411861Z 
2026-04-03T10:56:52.3412032Z ######################################################################
2026-04-03T10:56:52.3412460Z   HORIZON: 3 DAYS
2026-04-03T10:56:52.3412779Z ######################################################################
2026-04-03T10:56:52.3413341Z 
2026-04-03T10:56:52.3413594Z   ============================================================
2026-04-03T10:56:52.3414311Z   🛡️ Training PUT SAFETY model (3d, threshold ±2.5%)
2026-04-03T10:56:52.3414781Z   ============================================================
2026-04-03T10:56:52.3464819Z   📊 Class balance: SAFE=83.8% | BREACH=16.2%
2026-04-03T10:56:52.3465458Z   📊 Total samples: 2730
2026-04-03T10:56:52.3466070Z   🧠 Using Offline Master Chef recipes for PUT 3d
2026-04-03T10:56:54.1667608Z   ✅ CV Results: Accuracy=65.01% | LogLoss=0.6415
2026-04-03T10:56:54.6324470Z   💾 Saved: /home/runner/work/JUDAH-Nifty-Oracle/JUDAH-Nifty-Oracle/data/models/breach/xgb_breach_put_3d.pkl
2026-04-03T10:56:54.6625120Z   🎯 Final Validation: Accuracy=84.39% | LogLoss=0.4120
2026-04-03T10:56:54.6625789Z   📋 Classification Report:
2026-04-03T10:56:54.6700628Z               precision    recall  f1-score   support
2026-04-03T10:56:54.6701020Z 
2026-04-03T10:56:54.6701400Z    BREACH ⚠️       0.00      0.00      0.00        64
2026-04-03T10:56:54.6701991Z       SAFE ✅       0.84      1.00      0.92       346
2026-04-03T10:56:54.6702212Z 
2026-04-03T10:56:54.6702363Z     accuracy                           0.84       410
2026-04-03T10:56:54.6702711Z    macro avg       0.42      0.50      0.46       410
2026-04-03T10:56:54.6703087Z weighted avg       0.71      0.84      0.77       410
2026-04-03T10:56:54.6703336Z 
2026-04-03T10:56:54.6703340Z 
2026-04-03T10:56:54.6703464Z   ============================================================
2026-04-03T10:56:54.6704016Z   🛡️ Training CALL SAFETY model (3d, threshold ±2.5%)
2026-04-03T10:56:54.6704483Z   ============================================================
2026-04-03T10:56:54.6739719Z   📊 Class balance: SAFE=84.4% | BREACH=15.6%
2026-04-03T10:56:54.6741063Z   📊 Total samples: 2730
2026-04-03T10:56:54.6741397Z   🧠 Using Offline Master Chef recipes for CALL 3d
2026-04-03T10:56:56.4787800Z   ✅ CV Results: Accuracy=71.78% | LogLoss=0.6094
2026-04-03T10:56:56.9469661Z   💾 Saved: /home/runner/work/JUDAH-Nifty-Oracle/JUDAH-Nifty-Oracle/data/models/breach/xgb_breach_call_3d.pkl
2026-04-03T10:56:56.9764442Z   🎯 Final Validation: Accuracy=85.61% | LogLoss=0.3866
2026-04-03T10:56:56.9765119Z   📋 Classification Report:
2026-04-03T10:56:56.9836925Z               precision    recall  f1-score   support
2026-04-03T10:56:56.9839156Z 
2026-04-03T10:56:56.9840988Z    BREACH ⚠️       1.00      0.02      0.03        60
2026-04-03T10:56:56.9842441Z       SAFE ✅       0.86      1.00      0.92       350
2026-04-03T10:56:56.9844530Z 
2026-04-03T10:56:56.9844748Z     accuracy                           0.86       410
2026-04-03T10:56:56.9845287Z    macro avg       0.93      0.51      0.48       410
2026-04-03T10:56:56.9845784Z weighted avg       0.88      0.86      0.79       410
2026-04-03T10:56:56.9846083Z 
2026-04-03T10:56:56.9849701Z 
2026-04-03T10:56:56.9850074Z ######################################################################
2026-04-03T10:56:56.9850558Z   HORIZON: 5 DAYS
2026-04-03T10:56:56.9851161Z ######################################################################
2026-04-03T10:56:56.9852557Z 
2026-04-03T10:56:56.9852815Z   ============================================================
2026-04-03T10:56:56.9853522Z   🛡️ Training PUT SAFETY model (5d, threshold ±2.5%)
2026-04-03T10:56:56.9854030Z   ============================================================
2026-04-03T10:56:56.9904627Z   📊 Class balance: SAFE=73.7% | BREACH=26.3%
2026-04-03T10:56:56.9905140Z   📊 Total samples: 2730
2026-04-03T10:56:56.9905649Z   🧠 Using Offline Master Chef recipes for PUT 5d
2026-04-03T10:56:58.8228240Z   ✅ CV Results: Accuracy=59.91% | LogLoss=0.6632
2026-04-03T10:56:59.2881479Z   💾 Saved: /home/runner/work/JUDAH-Nifty-Oracle/JUDAH-Nifty-Oracle/data/models/breach/xgb_breach_put_5d.pkl
2026-04-03T10:56:59.3180504Z   🎯 Final Validation: Accuracy=70.73% | LogLoss=0.5974
2026-04-03T10:56:59.3182520Z   📋 Classification Report:
2026-04-03T10:56:59.3251225Z               precision    recall  f1-score   support
2026-04-03T10:56:59.3252091Z 
2026-04-03T10:56:59.3252526Z    BREACH ⚠️       0.60      0.02      0.05       121
2026-04-03T10:56:59.3253116Z       SAFE ✅       0.71      0.99      0.83       289
2026-04-03T10:56:59.3253415Z 
2026-04-03T10:56:59.3253551Z     accuracy                           0.71       410
2026-04-03T10:56:59.3253850Z    macro avg       0.65      0.51      0.44       410
2026-04-03T10:56:59.3254136Z weighted avg       0.68      0.71      0.60       410
2026-04-03T10:56:59.3254334Z 
2026-04-03T10:56:59.3254338Z 
2026-04-03T10:56:59.3254442Z   ============================================================
2026-04-03T10:56:59.3254828Z   🛡️ Training CALL SAFETY model (5d, threshold ±2.5%)
2026-04-03T10:56:59.3255139Z   ============================================================
2026-04-03T10:56:59.3290566Z   📊 Class balance: SAFE=72.4% | BREACH=27.6%
2026-04-03T10:56:59.3291195Z   📊 Total samples: 2730
2026-04-03T10:56:59.3291774Z   🧠 Using Offline Master Chef recipes for CALL 5d
2026-04-03T10:57:01.0707573Z   ✅ CV Results: Accuracy=62.51% | LogLoss=0.6542
2026-04-03T10:57:01.5285390Z   💾 Saved: /home/runner/work/JUDAH-Nifty-Oracle/JUDAH-Nifty-Oracle/data/models/breach/xgb_breach_call_5d.pkl
2026-04-03T10:57:01.5587069Z   🎯 Final Validation: Accuracy=74.88% | LogLoss=0.5367
2026-04-03T10:57:01.5587765Z   📋 Classification Report:
2026-04-03T10:57:01.5650681Z               precision    recall  f1-score   support
2026-04-03T10:57:01.5651257Z 
2026-04-03T10:57:01.5651597Z    BREACH ⚠️       1.00      0.01      0.02       104
2026-04-03T10:57:01.5655386Z       SAFE ✅       0.75      1.00      0.86       306
2026-04-03T10:57:01.5655749Z 
2026-04-03T10:57:01.5655893Z     accuracy                           0.75       410
2026-04-03T10:57:01.5656278Z    macro avg       0.87      0.50      0.44       410
2026-04-03T10:57:01.5656958Z weighted avg       0.81      0.75      0.64       410
2026-04-03T10:57:01.5657218Z 
2026-04-03T10:57:01.5663376Z 
2026-04-03T10:57:01.5663667Z ######################################################################
2026-04-03T10:57:01.5664168Z   HORIZON: 7 DAYS
2026-04-03T10:57:01.5664532Z ######################################################################
2026-04-03T10:57:01.5665413Z 
2026-04-03T10:57:01.5665902Z   ============================================================
2026-04-03T10:57:01.5666812Z   🛡️ Training PUT SAFETY model (7d, threshold ±2.5%)
2026-04-03T10:57:01.5667340Z   ============================================================
2026-04-03T10:57:01.5716549Z   📊 Class balance: SAFE=66.7% | BREACH=33.3%
2026-04-03T10:57:01.5717396Z   📊 Total samples: 2730
2026-04-03T10:57:01.5717983Z   🧠 Using Offline Master Chef recipes for PUT 7d
2026-04-03T10:57:03.4837751Z   ✅ CV Results: Accuracy=57.49% | LogLoss=0.6715
2026-04-03T10:57:03.7312762Z   💾 Saved: /home/runner/work/JUDAH-Nifty-Oracle/JUDAH-Nifty-Oracle/data/models/breach/xgb_breach_put_7d.pkl
2026-04-03T10:57:03.7607923Z   🎯 Final Validation: Accuracy=60.24% | LogLoss=0.6559
2026-04-03T10:57:03.7608949Z   📋 Classification Report:
2026-04-03T10:57:03.7680645Z               precision    recall  f1-score   support
2026-04-03T10:57:03.7683519Z 
2026-04-03T10:57:03.7686141Z    BREACH ⚠️       0.00      0.00      0.00       163
2026-04-03T10:57:03.7693029Z       SAFE ✅       0.60      1.00      0.75       247
2026-04-03T10:57:03.7693392Z 
2026-04-03T10:57:03.7693599Z     accuracy                           0.60       410
2026-04-03T10:57:03.7694124Z    macro avg       0.30      0.50      0.38       410
2026-04-03T10:57:03.7694655Z weighted avg       0.36      0.60      0.45       410
2026-04-03T10:57:03.7696639Z 
2026-04-03T10:57:03.7697912Z 
2026-04-03T10:57:03.7699380Z   ============================================================
2026-04-03T10:57:03.7701512Z   🛡️ Training CALL SAFETY model (7d, threshold ±2.5%)
2026-04-03T10:57:03.7703431Z   ============================================================
2026-04-03T10:57:03.7721684Z   📊 Class balance: SAFE=63.4% | BREACH=36.6%
2026-04-03T10:57:03.7723375Z   📊 Total samples: 2730
2026-04-03T10:57:03.7723998Z   🧠 Using Offline Master Chef recipes for CALL 7d
2026-04-03T10:57:05.4132813Z   ✅ CV Results: Accuracy=58.73% | LogLoss=0.6780
2026-04-03T10:57:05.8288135Z   💾 Saved: /home/runner/work/JUDAH-Nifty-Oracle/JUDAH-Nifty-Oracle/data/models/breach/xgb_breach_call_7d.pkl
2026-04-03T10:57:05.8582014Z   🎯 Final Validation: Accuracy=66.83% | LogLoss=0.6155
2026-04-03T10:57:05.8582614Z   📋 Classification Report:
2026-04-03T10:57:05.8653545Z               precision    recall  f1-score   support
2026-04-03T10:57:05.8653900Z 
2026-04-03T10:57:05.8654285Z    BREACH ⚠️       0.56      0.07      0.13       138
2026-04-03T10:57:05.8654976Z       SAFE ✅       0.67      0.97      0.80       272
2026-04-03T10:57:05.8655370Z 
2026-04-03T10:57:05.8655572Z     accuracy                           0.67       410
2026-04-03T10:57:05.8656219Z    macro avg       0.61      0.52      0.46       410
2026-04-03T10:57:05.8656948Z weighted avg       0.63      0.67      0.57       410
2026-04-03T10:57:05.8657248Z 
2026-04-03T10:57:05.8667532Z 
2026-04-03T10:57:05.8667742Z ######################################################################
2026-04-03T10:57:05.8668221Z   HORIZON: 14 DAYS
2026-04-03T10:57:05.8668597Z ######################################################################
2026-04-03T10:57:05.8669961Z 
2026-04-03T10:57:05.8670157Z   ============================================================
2026-04-03T10:57:05.8670830Z   🛡️ Training PUT SAFETY model (14d, threshold ±2.5%)
2026-04-03T10:57:05.8671352Z   ============================================================
2026-04-03T10:57:05.8721150Z   📊 Class balance: SAFE=52.7% | BREACH=47.3%
2026-04-03T10:57:05.8721777Z   📊 Total samples: 2730
2026-04-03T10:57:05.8722391Z   🧠 Using Offline Master Chef recipes for PUT 14d
2026-04-03T10:57:06.8827704Z   ✅ CV Results: Accuracy=48.88% | LogLoss=0.6985
2026-04-03T10:57:07.1218776Z   💾 Saved: /home/runner/work/JUDAH-Nifty-Oracle/JUDAH-Nifty-Oracle/data/models/breach/xgb_breach_put_14d.pkl
2026-04-03T10:57:07.1647067Z   🎯 Final Validation: Accuracy=58.05% | LogLoss=0.6799
2026-04-03T10:57:07.1649012Z   📋 Classification Report:
2026-04-03T10:57:07.1710396Z               precision    recall  f1-score   support
2026-04-03T10:57:07.1710921Z 
2026-04-03T10:57:07.1712007Z    BREACH ⚠️       0.58      1.00      0.73       238
2026-04-03T10:57:07.1712817Z       SAFE ✅       0.00      0.00      0.00       172
2026-04-03T10:57:07.1713247Z 
2026-04-03T10:57:07.1713495Z     accuracy                           0.58       410
2026-04-03T10:57:07.1714171Z    macro avg       0.29      0.50      0.37       410
2026-04-03T10:57:07.1714750Z weighted avg       0.34      0.58      0.43       410
2026-04-03T10:57:07.1715107Z 
2026-04-03T10:57:07.1715115Z 
2026-04-03T10:57:07.1715274Z   ============================================================
2026-04-03T10:57:07.1715962Z   🛡️ Training CALL SAFETY model (14d, threshold ±2.5%)
2026-04-03T10:57:07.1716826Z   ============================================================
2026-04-03T10:57:07.1748513Z   📊 Class balance: SAFE=42.8% | BREACH=57.2%
2026-04-03T10:57:07.1749129Z   📊 Total samples: 2730
2026-04-03T10:57:07.1749695Z   🧠 Using Offline Master Chef recipes for CALL 14d
2026-04-03T10:57:08.4957809Z   ✅ CV Results: Accuracy=47.56% | LogLoss=0.7046
2026-04-03T10:57:08.8349731Z   💾 Saved: /home/runner/work/JUDAH-Nifty-Oracle/JUDAH-Nifty-Oracle/data/models/breach/xgb_breach_call_14d.pkl
2026-04-03T10:57:08.8646134Z   🎯 Final Validation: Accuracy=55.61% | LogLoss=0.6790
2026-04-03T10:57:08.8647053Z   📋 Classification Report:
2026-04-03T10:57:08.8720003Z               precision    recall  f1-score   support
2026-04-03T10:57:08.8720381Z 
2026-04-03T10:57:08.8722124Z    BREACH ⚠️       0.57      0.46      0.51       206
2026-04-03T10:57:08.8723702Z       SAFE ✅       0.54      0.66      0.60       204
2026-04-03T10:57:08.8724023Z 
2026-04-03T10:57:08.8724192Z     accuracy                           0.56       410
2026-04-03T10:57:08.8724669Z    macro avg       0.56      0.56      0.55       410
2026-04-03T10:57:08.8725193Z weighted avg       0.56      0.56      0.55       410
2026-04-03T10:57:08.8725533Z 
2026-04-03T10:57:08.8734569Z 
2026-04-03T10:57:08.8736913Z ######################################################################
2026-04-03T10:57:08.8738564Z   HORIZON: 21 DAYS
2026-04-03T10:57:08.8738977Z ######################################################################
2026-04-03T10:57:08.8739342Z 
2026-04-03T10:57:08.8739522Z   ============================================================
2026-04-03T10:57:08.8740360Z   🛡️ Training PUT SAFETY model (21d, threshold ±2.5%)
2026-04-03T10:57:08.8740915Z   ============================================================
2026-04-03T10:57:08.8792269Z   📊 Class balance: SAFE=45.6% | BREACH=54.4%
2026-04-03T10:57:08.8792875Z   📊 Total samples: 2730
2026-04-03T10:57:08.8793459Z   🧠 Using Offline Master Chef recipes for PUT 21d
2026-04-03T10:57:09.8777964Z   ✅ CV Results: Accuracy=50.11% | LogLoss=0.6982
2026-04-03T10:57:10.0903568Z   💾 Saved: /home/runner/work/JUDAH-Nifty-Oracle/JUDAH-Nifty-Oracle/data/models/breach/xgb_breach_put_21d.pkl
2026-04-03T10:57:10.1193241Z   🎯 Final Validation: Accuracy=64.63% | LogLoss=0.6454
2026-04-03T10:57:10.1193903Z   📋 Classification Report:
2026-04-03T10:57:10.1266173Z               precision    recall  f1-score   support
2026-04-03T10:57:10.1267903Z 
2026-04-03T10:57:10.1269330Z    BREACH ⚠️       0.65      1.00      0.79       265
2026-04-03T10:57:10.1270839Z       SAFE ✅       0.00      0.00      0.00       145
2026-04-03T10:57:10.1272099Z 
2026-04-03T10:57:10.1273269Z     accuracy                           0.65       410
2026-04-03T10:57:10.1274493Z    macro avg       0.32      0.50      0.39       410
2026-04-03T10:57:10.1275610Z weighted avg       0.42      0.65      0.51       410
2026-04-03T10:57:10.1276867Z 
2026-04-03T10:57:10.1277710Z 
2026-04-03T10:57:10.1278653Z   ============================================================
2026-04-03T10:57:10.1280229Z   🛡️ Training CALL SAFETY model (21d, threshold ±2.5%)
2026-04-03T10:57:10.1280887Z   ============================================================
2026-04-03T10:57:10.1306085Z   📊 Class balance: SAFE=33.6% | BREACH=66.4%
2026-04-03T10:57:10.1307109Z   📊 Total samples: 2730
2026-04-03T10:57:10.1308307Z   🧠 Using Offline Master Chef recipes for CALL 21d
2026-04-03T10:57:11.4527643Z   ✅ CV Results: Accuracy=40.57% | LogLoss=0.7161
2026-04-03T10:57:11.9096839Z   💾 Saved: /home/runner/work/JUDAH-Nifty-Oracle/JUDAH-Nifty-Oracle/data/models/breach/xgb_breach_call_21d.pkl
2026-04-03T10:57:11.9390702Z   🎯 Final Validation: Accuracy=66.10% | LogLoss=0.6320
2026-04-03T10:57:11.9391379Z   📋 Classification Report:
2026-04-03T10:57:11.9464809Z               precision    recall  f1-score   support
2026-04-03T10:57:11.9465170Z 
2026-04-03T10:57:11.9465485Z    BREACH ⚠️       0.66      1.00      0.79       266
2026-04-03T10:57:11.9466025Z       SAFE ✅       0.86      0.04      0.08       144
2026-04-03T10:57:11.9466322Z 
2026-04-03T10:57:11.9467023Z     accuracy                           0.66       410
2026-04-03T10:57:11.9467527Z    macro avg       0.76      0.52      0.44       410
2026-04-03T10:57:11.9468070Z weighted avg       0.73      0.66      0.54       410
2026-04-03T10:57:11.9468415Z 
2026-04-03T10:57:11.9480701Z 
2026-04-03T10:57:11.9481037Z ######################################################################
2026-04-03T10:57:11.9481362Z   HORIZON: 30 DAYS
2026-04-03T10:57:11.9481599Z ######################################################################
2026-04-03T10:57:11.9484092Z 
2026-04-03T10:57:11.9484320Z   ============================================================
2026-04-03T10:57:11.9485250Z   🛡️ Training PUT SAFETY model (30d, threshold ±2.5%)
2026-04-03T10:57:11.9485909Z   ============================================================
2026-04-03T10:57:11.9537242Z   📊 Class balance: SAFE=41.6% | BREACH=58.4%
2026-04-03T10:57:11.9538022Z   📊 Total samples: 2730
2026-04-03T10:57:11.9538776Z   🧠 Using Offline Master Chef recipes for PUT 30d
2026-04-03T10:57:12.7697875Z   ✅ CV Results: Accuracy=45.85% | LogLoss=0.6990
2026-04-03T10:57:12.9816616Z   💾 Saved: /home/runner/work/JUDAH-Nifty-Oracle/JUDAH-Nifty-Oracle/data/models/breach/xgb_breach_put_30d.pkl
2026-04-03T10:57:13.0106717Z   🎯 Final Validation: Accuracy=69.76% | LogLoss=0.6121
2026-04-03T10:57:13.0107571Z   📋 Classification Report:
2026-04-03T10:57:13.0179132Z               precision    recall  f1-score   support
2026-04-03T10:57:13.0181097Z 
2026-04-03T10:57:13.0182830Z    BREACH ⚠️       0.70      1.00      0.82       286
2026-04-03T10:57:13.0184775Z       SAFE ✅       0.00      0.00      0.00       124
2026-04-03T10:57:13.0186749Z 
2026-04-03T10:57:13.0188308Z     accuracy                           0.70       410
2026-04-03T10:57:13.0191305Z    macro avg       0.35      0.50      0.41       410
2026-04-03T10:57:13.0193285Z weighted avg       0.49      0.70      0.57       410
2026-04-03T10:57:13.0193809Z 
2026-04-03T10:57:13.0194002Z 
2026-04-03T10:57:13.0194232Z   ============================================================
2026-04-03T10:57:13.0194987Z   🛡️ Training CALL SAFETY model (30d, threshold ±2.5%)
2026-04-03T10:57:13.0195563Z   ============================================================
2026-04-03T10:57:13.0220370Z   📊 Class balance: SAFE=27.0% | BREACH=73.0%
2026-04-03T10:57:13.0221146Z   📊 Total samples: 2730
2026-04-03T10:57:13.0221877Z   🧠 Using Offline Master Chef recipes for CALL 30d
2026-04-03T10:57:14.6567676Z   ✅ CV Results: Accuracy=63.03% | LogLoss=0.6688
2026-04-03T10:57:15.1215103Z   💾 Saved: /home/runner/work/JUDAH-Nifty-Oracle/JUDAH-Nifty-Oracle/data/models/breach/xgb_breach_call_30d.pkl
2026-04-03T10:57:15.1510232Z   🎯 Final Validation: Accuracy=67.32% | LogLoss=0.6279
2026-04-03T10:57:15.1511097Z   📋 Classification Report:
2026-04-03T10:57:15.1583918Z               precision    recall  f1-score   support
2026-04-03T10:57:15.1584274Z 
2026-04-03T10:57:15.1584634Z    BREACH ⚠️       0.67      1.00      0.80       276
2026-04-03T10:57:15.1585195Z       SAFE ✅       0.00      0.00      0.00       134
2026-04-03T10:57:15.1585490Z 
2026-04-03T10:57:15.1585645Z     accuracy                           0.67       410
2026-04-03T10:57:15.1586085Z    macro avg       0.34      0.50      0.40       410
2026-04-03T10:57:15.1587128Z weighted avg       0.45      0.67      0.54       410
2026-04-03T10:57:15.1587499Z 
2026-04-03T10:57:15.1601416Z 
2026-04-03T10:57:15.1602567Z 💎 Breach summary saved: /home/runner/work/JUDAH-Nifty-Oracle/JUDAH-Nifty-Oracle/data/models/breach/breach_summary.json
2026-04-03T10:57:15.1603353Z 
2026-04-03T10:57:15.1603584Z 🎉 BREACH RADAR training complete!
2026-04-03T10:57:15.2852664Z ##[group]Run python scripts/backtest_breach.py
2026-04-03T10:57:15.2853032Z [36;1mpython scripts/backtest_breach.py[0m
2026-04-03T10:57:15.2879920Z shell: /usr/bin/bash -e {0}
2026-04-03T10:57:15.2880147Z env:
2026-04-03T10:57:15.2880407Z   pythonLocation: /opt/hostedtoolcache/Python/3.12.13/x64
2026-04-03T10:57:15.2880839Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.12.13/x64/lib/pkgconfig
2026-04-03T10:57:15.2881428Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.13/x64
2026-04-03T10:57:15.2881781Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.13/x64
2026-04-03T10:57:15.2882141Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.13/x64
2026-04-03T10:57:15.2882522Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.12.13/x64/lib
2026-04-03T10:57:15.2882843Z   PYTHONUNBUFFERED: 1
2026-04-03T10:57:15.2883049Z   PYTHONIOENCODING: utf-8
2026-04-03T10:57:15.2883256Z ##[endgroup]
2026-04-03T10:57:16.3386088Z ======================================================================
2026-04-03T10:57:16.3387365Z   BREACH RADAR BACKTEST — Walk-Forward (No Look-Ahead)
2026-04-03T10:57:16.3387887Z   Period: 2023-01-01 to present
2026-04-03T10:57:16.3388335Z   Safety threshold: P(safe) >= 65%
2026-04-03T10:57:16.3388785Z   Breach threshold: +/-2.5% (~600 pts)
2026-04-03T10:57:16.3389228Z   Credit: 15.0 pts | Max Loss: 100.0 pts
2026-04-03T10:57:16.3389753Z ======================================================================
2026-04-03T10:57:16.3390200Z 
2026-04-03T10:57:16.3390333Z Building features...
2026-04-03T10:57:19.3174530Z Loaded 2730 rows.
2026-04-03T10:57:19.3174809Z 
2026-04-03T10:57:19.3175043Z ######################################################################
2026-04-03T10:57:19.3175536Z   HORIZON: 3 DAYS
2026-04-03T10:57:19.3175922Z ######################################################################
2026-04-03T10:57:47.7021924Z 
2026-04-03T10:57:47.7022344Z   ============================================================
2026-04-03T10:57:47.7022859Z   Bull Put Spread (3d)
2026-04-03T10:57:47.7023108Z   ============================================================
2026-04-03T10:57:47.7023397Z   Total Trades:      619
2026-04-03T10:57:47.7023608Z   Wins/Losses:       583/36
2026-04-03T10:57:47.7024022Z   Win Rate:          [92m94.2%[0m
2026-04-03T10:57:47.7024318Z   Total P/L:         [91m-505 pts[0m
2026-04-03T10:57:47.7024615Z   Avg P/L per trade: -0.8 pts
2026-04-03T10:57:47.7024847Z   Max Drawdown:      -960 pts
2026-04-03T10:57:47.7025062Z   Avg P(safe) at entry: 86.0%
2026-04-03T10:57:47.7025270Z   Signals/Month:     16.7
2026-04-03T10:57:47.7025466Z   Max Win Streak:    147
2026-04-03T10:57:47.7025671Z   Max Loss Streak:   4
2026-04-03T10:57:47.7048341Z 
2026-04-03T10:57:47.7048492Z   Worst 5 Losses:
2026-04-03T10:57:47.7053549Z     2026-02-06 | Spot 25,674 | Excursion -10.59% | P(safe) was 84.6%
2026-04-03T10:57:47.7054322Z     2024-06-03 | Spot 23,306 | Excursion -8.69% | P(safe) was 81.8%
2026-04-03T10:57:47.7055056Z     2025-04-02 | Spot 23,331 | Excursion -6.80% | P(safe) was 84.6%
2026-04-03T10:57:47.7056005Z     2025-04-03 | Spot 23,242 | Excursion -6.45% | P(safe) was 71.1%
2026-04-03T10:57:47.7057237Z     2025-04-04 | Spot 22,912 | Excursion -5.10% | P(safe) was 71.1%
2026-04-03T10:57:47.7215253Z 
2026-04-03T10:57:47.7215572Z   Monthly Breakdown:
2026-04-03T10:57:47.7215996Z   Month       Trades   Wins      P/L
2026-04-03T10:57:47.7216754Z   -----------------------------------
2026-04-03T10:57:47.7218951Z   2023-01         21     18     -195
2026-04-03T10:57:47.7219630Z   2023-02         19     19      +95
2026-04-03T10:57:47.7220738Z   2023-03         21     18     -195
2026-04-03T10:57:47.7221680Z   2023-04         17     17      +85
2026-04-03T10:57:47.7222640Z   2023-05         21     21     +105
2026-04-03T10:57:47.7223591Z   2023-06         21     21     +105
2026-04-03T10:57:47.7224499Z   2023-07         21     21     +105
2026-04-03T10:57:47.7225419Z   2023-08         22     22     +110
2026-04-03T10:57:47.7227084Z   2023-09         19     19      +95
2026-04-03T10:57:47.7227713Z   2023-10         20     18     -100
2026-04-03T10:57:47.7228426Z   2023-11         21     21     +105
2026-04-03T10:57:47.7229207Z   2023-12          3      3      +15
2026-04-03T10:57:47.7229999Z   2024-01         10      8     -150
2026-04-03T10:57:47.7230771Z   2024-02         10     10      +50
2026-04-03T10:57:47.7231612Z   2024-03         19     18       -5
2026-04-03T10:57:47.7232426Z   2024-04         17     16      -15
2026-04-03T10:57:47.7233309Z   2024-06         14     13      -30
2026-04-03T10:57:47.7234198Z   2024-07         20     18     -100
2026-04-03T10:57:47.7235095Z   2024-08         14     12     -130
2026-04-03T10:57:47.7235987Z   2024-09         21     19      -95
2026-04-03T10:57:47.7237085Z   2024-10         16     15      -20
2026-04-03T10:57:47.7238038Z   2024-11          8      7      -60
2026-04-03T10:57:47.7238967Z   2024-12         21     17     -295
2026-04-03T10:57:47.7239867Z   2025-01         12     10     -140
2026-04-03T10:57:47.7240771Z   2025-02         17     15     -115
2026-04-03T10:57:47.7241669Z   2025-03         19     19      +95
2026-04-03T10:57:47.7242571Z   2025-04          7      4     -265
2026-04-03T10:57:47.7243471Z   2025-05         10     10      +50
2026-04-03T10:57:47.7244352Z   2025-06         21     20       +5
2026-04-03T10:57:47.7245266Z   2025-07         23     23     +115
2026-04-03T10:57:47.7246136Z   2025-08         18     18      +90
2026-04-03T10:57:47.7247262Z   2025-09         22     22     +110
2026-04-03T10:57:47.7248225Z   2025-10         21     21     +105
2026-04-03T10:57:47.7249100Z   2025-11         18     18      +90
2026-04-03T10:57:47.7250007Z   2025-12         22     22     +110
2026-04-03T10:57:47.7250907Z   2026-01         12     10     -140
2026-04-03T10:57:47.7251790Z   2026-02          1      0      -95
2026-04-03T10:58:15.5965579Z 
2026-04-03T10:58:15.5965940Z   ============================================================
2026-04-03T10:58:15.5966286Z   Bear Call Spread (3d)
2026-04-03T10:58:15.5966783Z   ============================================================
2026-04-03T10:58:15.5967060Z   Total Trades:      584
2026-04-03T10:58:15.5967273Z   Wins/Losses:       571/13
2026-04-03T10:58:15.5967708Z   Win Rate:          [92m97.8%[0m
2026-04-03T10:58:15.5968003Z   Total P/L:         [92m+1620 pts[0m
2026-04-03T10:58:15.5968258Z   Avg P/L per trade: +2.8 pts
2026-04-03T10:58:15.5968495Z   Max Drawdown:      0 pts
2026-04-03T10:58:15.5968703Z   Avg P(safe) at entry: 87.3%
2026-04-03T10:58:15.5968920Z   Signals/Month:     15.8
2026-04-03T10:58:15.5969122Z   Max Win Streak:    146
2026-04-03T10:58:15.5969315Z   Max Loss Streak:   2
2026-04-03T10:58:15.5990735Z 
2026-04-03T10:58:15.5990886Z   Worst 5 Losses:
2026-04-03T10:58:15.5995749Z     2025-03-04 | Spot 22,080 | Excursion +2.51% | P(safe) was 81.0%
2026-04-03T10:58:15.5996726Z     2025-10-14 | Spot 25,123 | Excursion +2.62% | P(safe) was 81.0%
2026-04-03T10:58:15.5997515Z     2023-03-29 | Spot 17,116 | Excursion +2.65% | P(safe) was 81.8%
2026-04-03T10:58:15.5998490Z     2023-03-02 | Spot 17,319 | Excursion +2.77% | P(safe) was 81.0%
2026-04-03T10:58:15.5999347Z     2023-03-28 | Spot 16,957 | Excursion +2.78% | P(safe) was 81.0%
2026-04-03T10:58:15.6150459Z 
2026-04-03T10:58:15.6150648Z   Monthly Breakdown:
2026-04-03T10:58:15.6151115Z   Month       Trades   Wins      P/L
2026-04-03T10:58:15.6151492Z   -----------------------------------
2026-04-03T10:58:15.6153468Z   2023-01         21     21     +105
2026-04-03T10:58:15.6154092Z   2023-02         19     19      +95
2026-04-03T10:58:15.6155026Z   2023-03         21     18     -195
2026-04-03T10:58:15.6156025Z   2023-04         17     17      +85
2026-04-03T10:58:15.6157134Z   2023-05         19     19      +95
2026-04-03T10:58:15.6158023Z   2023-06         15     15      +75
2026-04-03T10:58:15.6158966Z   2023-07         20     20     +100
2026-04-03T10:58:15.6159840Z   2023-08         21     21     +105
2026-04-03T10:58:15.6160674Z   2023-09         18     18      +90
2026-04-03T10:58:15.6161746Z   2023-10         17     17      +85
2026-04-03T10:58:15.6162301Z   2023-11         20     18     -100
2026-04-03T10:58:15.6163046Z   2023-12          1      1       +5
2026-04-03T10:58:15.6163937Z   2024-01          9      9      +45
2026-04-03T10:58:15.6164871Z   2024-02         10     10      +50
2026-04-03T10:58:15.6165764Z   2024-03         19     19      +95
2026-04-03T10:58:15.6167039Z   2024-04         17     17      +85
2026-04-03T10:58:15.6167983Z   2024-06         14     14      +70
2026-04-03T10:58:15.6168893Z   2024-07         20     20     +100
2026-04-03T10:58:15.6169798Z   2024-08         14     14      +70
2026-04-03T10:58:15.6170641Z   2024-09         19     19      +95
2026-04-03T10:58:15.6171554Z   2024-10         15     15      +75
2026-04-03T10:58:15.6172442Z   2024-11          8      7      -60
2026-04-03T10:58:15.6173291Z   2024-12         21     21     +105
2026-04-03T10:58:15.6174211Z   2025-01         12     12      +60
2026-04-03T10:58:15.6175045Z   2025-02         17     17      +85
2026-04-03T10:58:15.6175980Z   2025-03         19     15     -305
2026-04-03T10:58:15.6177063Z   2025-04          7      6      -65
2026-04-03T10:58:15.6178023Z   2025-05         10      9      -50
2026-04-03T10:58:15.6178944Z   2025-06         21     21     +105
2026-04-03T10:58:15.6179882Z   2025-07         23     23     +115
2026-04-03T10:58:15.6180703Z   2025-08         17     17      +85
2026-04-03T10:58:15.6181612Z   2025-09         18     18      +90
2026-04-03T10:58:15.6182511Z   2025-10         19     18       -5
2026-04-03T10:58:15.6183412Z   2025-11         18     18      +90
2026-04-03T10:58:15.6184288Z   2025-12         17     17      +85
2026-04-03T10:58:15.6185133Z   2026-01         10     10      +50
2026-04-03T10:58:15.6186049Z   2026-02          1      1       +5
2026-04-03T10:58:15.6186454Z 
2026-04-03T10:58:15.6186682Z ######################################################################
2026-04-03T10:58:15.6187182Z   HORIZON: 5 DAYS
2026-04-03T10:58:15.6187417Z ######################################################################
2026-04-03T10:58:43.7353376Z 
2026-04-03T10:58:43.7353768Z   ============================================================
2026-04-03T10:58:43.7354305Z   Bull Put Spread (5d)
2026-04-03T10:58:43.7354547Z   ============================================================
2026-04-03T10:58:43.7354839Z   Total Trades:      594
2026-04-03T10:58:43.7355086Z   Wins/Losses:       525/69
2026-04-03T10:58:43.7355505Z   Win Rate:          [92m88.4%[0m
2026-04-03T10:58:43.7355797Z   Total P/L:         [91m-3930 pts[0m
2026-04-03T10:58:43.7356066Z   Avg P/L per trade: -6.6 pts
2026-04-03T10:58:43.7356521Z   Max Drawdown:      -3930 pts
2026-04-03T10:58:43.7356815Z   Avg P(safe) at entry: 72.6%
2026-04-03T10:58:43.7357033Z   Signals/Month:     16.1
2026-04-03T10:58:43.7357234Z   Max Win Streak:    125
2026-04-03T10:58:43.7357426Z   Max Loss Streak:   6
2026-04-03T10:58:43.7378711Z 
2026-04-03T10:58:43.7378858Z   Worst 5 Losses:
2026-04-03T10:58:43.7383382Z     2026-02-06 | Spot 25,674 | Excursion -10.68% | P(safe) was 69.2%
2026-04-03T10:58:43.7384228Z     2025-03-28 | Spot 23,495 | Excursion -7.45% | P(safe) was 69.2%
2026-04-03T10:58:43.7385038Z     2025-04-02 | Spot 23,331 | Excursion -6.80% | P(safe) was 69.2%
2026-04-03T10:58:43.7385888Z     2025-04-03 | Spot 23,242 | Excursion -6.45% | P(safe) was 69.2%
2026-04-03T10:58:43.7386863Z     2025-04-01 | Spot 23,180 | Excursion -6.20% | P(safe) was 69.2%
2026-04-03T10:58:43.7540518Z 
2026-04-03T10:58:43.7540715Z   Monthly Breakdown:
2026-04-03T10:58:43.7541146Z   Month       Trades   Wins      P/L
2026-04-03T10:58:43.7541658Z   -----------------------------------
2026-04-03T10:58:43.7543467Z   2023-01         21     16     -395
2026-04-03T10:58:43.7544210Z   2023-02         19     14     -405
2026-04-03T10:58:43.7545106Z   2023-03         21     16     -395
2026-04-03T10:58:43.7545983Z   2023-04         17     17      +85
2026-04-03T10:58:43.7547104Z   2023-05         21     21     +105
2026-04-03T10:58:43.7548511Z   2023-06         21     21     +105
2026-04-03T10:58:43.7548974Z   2023-07         21     21     +105
2026-04-03T10:58:43.7549895Z   2023-08         22     22     +110
2026-04-03T10:58:43.7550778Z   2023-09         14     12     -130
2026-04-03T10:58:43.7551622Z   2023-10         13     13      +65
2026-04-03T10:58:43.7552482Z   2023-11         21     21     +105
2026-04-03T10:58:43.7553304Z   2023-12          3      3      +15
2026-04-03T10:58:43.7554190Z   2024-01         10      7     -250
2026-04-03T10:58:43.7555015Z   2024-02         10     10      +50
2026-04-03T10:58:43.7555888Z   2024-03         19     17     -105
2026-04-03T10:58:43.7556719Z   2024-04         10      9      -50
2026-04-03T10:58:43.7557868Z   2024-06         13     13      +65
2026-04-03T10:58:43.7558658Z   2024-07         20     16     -300
2026-04-03T10:58:43.7559520Z   2024-08         14     12     -130
2026-04-03T10:58:43.7560347Z   2024-09         21     17     -295
2026-04-03T10:58:43.7561189Z   2024-10         16     12     -320
2026-04-03T10:58:43.7562022Z   2024-11          8      7      -60
2026-04-03T10:58:43.7562926Z   2024-12         21     16     -395
2026-04-03T10:58:43.7563727Z   2025-01         12      9     -240
2026-04-03T10:58:43.7564654Z   2025-02         17     11     -515
2026-04-03T10:58:43.7565416Z   2025-03         19     17     -105
2026-04-03T10:58:43.7566281Z   2025-04          7      3     -365
2026-04-03T10:58:43.7567377Z   2025-05          9      9      +45
2026-04-03T10:58:43.7568192Z   2025-06         21     19      -95
2026-04-03T10:58:43.7569055Z   2025-07         23     23     +115
2026-04-03T10:58:43.7569873Z   2025-08         18     17      -10
2026-04-03T10:58:43.7570769Z   2025-09         21     20       +5
2026-04-03T10:58:43.7571542Z   2025-10         21     21     +105
2026-04-03T10:58:43.7572454Z   2025-11         18     18      +90
2026-04-03T10:58:43.7573224Z   2025-12         22     22     +110
2026-04-03T10:58:43.7574063Z   2026-01          9      3     -555
2026-04-03T10:58:43.7574867Z   2026-02          1      0      -95
2026-04-03T10:59:12.0504092Z 
2026-04-03T10:59:12.0504531Z   ============================================================
2026-04-03T10:59:12.0505084Z   Bear Call Spread (5d)
2026-04-03T10:59:12.0505323Z   ============================================================
2026-04-03T10:59:12.0505605Z   Total Trades:      505
2026-04-03T10:59:12.0506020Z   Wins/Losses:       473/32
2026-04-03T10:59:12.0506942Z   Win Rate:          [92m93.7%[0m
2026-04-03T10:59:12.0507431Z   Total P/L:         [91m-675 pts[0m
2026-04-03T10:59:12.0507696Z   Avg P/L per trade: -1.3 pts
2026-04-03T10:59:12.0507926Z   Max Drawdown:      -900 pts
2026-04-03T10:59:12.0508143Z   Avg P(safe) at entry: 79.3%
2026-04-03T10:59:12.0508355Z   Signals/Month:     13.6
2026-04-03T10:59:12.0508553Z   Max Win Streak:    68
2026-04-03T10:59:12.0508750Z   Max Loss Streak:   6
2026-04-03T10:59:12.0529450Z 
2026-04-03T10:59:12.0529583Z   Worst 5 Losses:
2026-04-03T10:59:12.0534125Z     2023-09-06 | Spot 19,619 | Excursion +2.50% | P(safe) was 75.4%
2026-04-03T10:59:12.0534934Z     2024-04-18 | Spot 22,046 | Excursion +2.63% | P(safe) was 74.8%
2026-04-03T10:59:12.0535689Z     2024-06-24 | Spot 23,549 | Excursion +2.66% | P(safe) was 83.7%
2026-04-03T10:59:12.0536769Z     2023-04-21 | Spot 17,619 | Excursion +2.67% | P(safe) was 74.8%
2026-04-03T10:59:12.0537684Z     2025-06-03 | Spot 24,538 | Excursion +2.69% | P(safe) was 74.8%
2026-04-03T10:59:12.0686377Z 
2026-04-03T10:59:12.0686584Z   Monthly Breakdown:
2026-04-03T10:59:12.0687056Z   Month       Trades   Wins      P/L
2026-04-03T10:59:12.0687846Z   -----------------------------------
2026-04-03T10:59:12.0689625Z   2023-01         21     21     +105
2026-04-03T10:59:12.0690338Z   2023-02         18     18      +90
2026-04-03T10:59:12.0691275Z   2023-03         18     15     -210
2026-04-03T10:59:12.0692212Z   2023-04         13     12      -35
2026-04-03T10:59:12.0693052Z   2023-05         12     12      +60
2026-04-03T10:59:12.0693920Z   2023-06         12     12      +60
2026-04-03T10:59:12.0695159Z   2023-07         17     16      -15
2026-04-03T10:59:12.0695598Z   2023-08         20     20     +100
2026-04-03T10:59:12.0696495Z   2023-09         17     15     -115
2026-04-03T10:59:12.0697593Z   2023-10         11     11      +55
2026-04-03T10:59:12.0698410Z   2023-11         13     13      +65
2026-04-03T10:59:12.0699350Z   2023-12          1      1       +5
2026-04-03T10:59:12.0700142Z   2024-01          5      5      +25
2026-04-03T10:59:12.0701014Z   2024-02         10     10      +50
2026-04-03T10:59:12.0701835Z   2024-03         19     18       -5
2026-04-03T10:59:12.0702709Z   2024-04         17     16      -15
2026-04-03T10:59:12.0703525Z   2024-06         13     11     -135
2026-04-03T10:59:12.0704358Z   2024-07         18     18      +90
2026-04-03T10:59:12.0705174Z   2024-08         14     14      +70
2026-04-03T10:59:12.0706030Z   2024-09         18     16     -110
2026-04-03T10:59:12.0707159Z   2024-10         13     13      +65
2026-04-03T10:59:12.0707980Z   2024-11          7      4     -265
2026-04-03T10:59:12.0708846Z   2024-12         18     18      +90
2026-04-03T10:59:12.0709684Z   2025-01         11      9     -145
2026-04-03T10:59:12.0710531Z   2025-02         17     17      +85
2026-04-03T10:59:12.0711351Z   2025-03         19     12     -605
2026-04-03T10:59:12.0712198Z   2025-04          6      6      +30
2026-04-03T10:59:12.0713001Z   2025-05         10      9      -50
2026-04-03T10:59:12.0713849Z   2025-06         21     18     -195
2026-04-03T10:59:12.0714643Z   2025-07         16     16      +80
2026-04-03T10:59:12.0715500Z   2025-08          9      9      +45
2026-04-03T10:59:12.0716313Z   2025-09         17     17      +85
2026-04-03T10:59:12.0717441Z   2025-10         20     17     -200
2026-04-03T10:59:12.0718220Z   2025-11         13     13      +65
2026-04-03T10:59:12.0719117Z   2025-12         15     15      +75
2026-04-03T10:59:12.0719895Z   2026-01          5      5      +25
2026-04-03T10:59:12.0720743Z   2026-02          1      1       +5
2026-04-03T10:59:12.0721138Z 
2026-04-03T10:59:12.0721314Z ######################################################################
2026-04-03T10:59:12.0721764Z   HORIZON: 7 DAYS
2026-04-03T10:59:12.0722122Z ######################################################################
2026-04-03T10:59:40.2463439Z 
2026-04-03T10:59:40.2477302Z   ============================================================
2026-04-03T10:59:40.2477853Z   Bull Put Spread (7d)
2026-04-03T10:59:40.2478227Z   ============================================================
2026-04-03T10:59:40.2478686Z   Total Trades:      39
2026-04-03T10:59:40.2479051Z   Wins/Losses:       37/2
2026-04-03T10:59:40.2479647Z   Win Rate:          [92m94.9%[0m
2026-04-03T10:59:40.2480118Z   Total P/L:         [91m-5 pts[0m
2026-04-03T10:59:40.2480548Z   Avg P/L per trade: -0.1 pts
2026-04-03T10:59:40.2480933Z   Max Drawdown:      -95 pts
2026-04-03T10:59:40.2481299Z   Avg P(safe) at entry: 81.9%
2026-04-03T10:59:40.2481663Z   Signals/Month:     3.9
2026-04-03T10:59:40.2482021Z   Max Win Streak:    19
2026-04-03T10:59:40.2482347Z   Max Loss Streak:   2
2026-04-03T10:59:40.2483105Z 
2026-04-03T10:59:40.2483236Z   Worst 5 Losses:
2026-04-03T10:59:40.2497871Z     2024-07-26 | Spot 24,852 | Excursion -3.86% | P(safe) was 73.7%
2026-04-03T10:59:40.2498624Z     2024-07-29 | Spot 24,841 | Excursion -3.81% | P(safe) was 73.7%
2026-04-03T10:59:40.2571563Z 
2026-04-03T10:59:40.2571785Z   Monthly Breakdown:
2026-04-03T10:59:40.2572154Z   Month       Trades   Wins      P/L
2026-04-03T10:59:40.2572570Z   -----------------------------------
2026-04-03T10:59:40.2574406Z   2023-02          1      1       +5
2026-04-03T10:59:40.2575168Z   2023-03          3      3      +15
2026-04-03T10:59:40.2576115Z   2023-04          3      3      +15
2026-04-03T10:59:40.2577211Z   2023-05          8      8      +40
2026-04-03T10:59:40.2578145Z   2024-06          2      2      +10
2026-04-03T10:59:40.2578962Z   2024-07          4      2     -180
2026-04-03T10:59:40.2580197Z   2024-08         11     11      +55
2026-04-03T10:59:40.2580701Z   2024-11          1      1       +5
2026-04-03T10:59:40.2581553Z   2024-12          5      5      +25
2026-04-03T10:59:40.2582391Z   2025-01          1      1       +5
2026-04-03T11:00:08.2304847Z 
2026-04-03T11:00:08.2307816Z   ============================================================
2026-04-03T11:00:08.2308428Z   Bear Call Spread (7d)
2026-04-03T11:00:08.2311229Z   ============================================================
2026-04-03T11:00:08.2311729Z   Total Trades:      313
2026-04-03T11:00:08.2312107Z   Wins/Losses:       280/33
2026-04-03T11:00:08.2312784Z   Win Rate:          [92m89.5%[0m
2026-04-03T11:00:08.2313291Z   Total P/L:         [91m-1735 pts[0m
2026-04-03T11:00:08.2313726Z   Avg P/L per trade: -5.5 pts
2026-04-03T11:00:08.2314131Z   Max Drawdown:      -1970 pts
2026-04-03T11:00:08.2314538Z   Avg P(safe) at entry: 75.9%
2026-04-03T11:00:08.2314933Z   Signals/Month:     8.9
2026-04-03T11:00:08.2315301Z   Max Win Streak:    47
2026-04-03T11:00:08.2315668Z   Max Loss Streak:   8
2026-04-03T11:00:08.2329693Z 
2026-04-03T11:00:08.2330103Z   Worst 5 Losses:
2026-04-03T11:00:08.2334389Z     2024-06-20 | Spot 23,579 | Excursion +2.52% | P(safe) was 84.6%
2026-04-03T11:00:08.2335051Z     2023-09-07 | Spot 19,723 | Excursion +2.53% | P(safe) was 75.0%
2026-04-03T11:00:08.2336005Z     2023-04-03 | Spot 17,400 | Excursion +2.66% | P(safe) was 84.6%
2026-04-03T11:00:08.2336964Z     2025-03-04 | Spot 22,080 | Excursion +2.70% | P(safe) was 65.4%
2026-04-03T11:00:08.2337987Z     2024-03-26 | Spot 22,018 | Excursion +2.73% | P(safe) was 71.2%
2026-04-03T11:00:08.2472764Z 
2026-04-03T11:00:08.2473007Z   Monthly Breakdown:
2026-04-03T11:00:08.2473491Z   Month       Trades   Wins      P/L
2026-04-03T11:00:08.2474066Z   -----------------------------------
2026-04-03T11:00:08.2475459Z   2023-01         20     20     +100
2026-04-03T11:00:08.2476301Z   2023-02         19     18       -5
2026-04-03T11:00:08.2477479Z   2023-03          9      7     -155
2026-04-03T11:00:08.2478358Z   2023-04          9      8      -55
2026-04-03T11:00:08.2479250Z   2023-05          2      2      +10
2026-04-03T11:00:08.2480000Z   2023-06          2      2      +10
2026-04-03T11:00:08.2480870Z   2023-07          6      6      +30
2026-04-03T11:00:08.2481686Z   2023-08         14     14      +70
2026-04-03T11:00:08.2482539Z   2023-09         17     14     -215
2026-04-03T11:00:08.2483364Z   2023-10          4      4      +20
2026-04-03T11:00:08.2484197Z   2024-01          2      2      +10
2026-04-03T11:00:08.2485029Z   2024-02         10      9      -50
2026-04-03T11:00:08.2485877Z   2024-03         15     14      -25
2026-04-03T11:00:08.2486711Z   2024-04         13     13      +65
2026-04-03T11:00:08.2487808Z   2024-06         13      8     -435
2026-04-03T11:00:08.2488587Z   2024-07          6      6      +30
2026-04-03T11:00:08.2489510Z   2024-08         12     12      +60
2026-04-03T11:00:08.2490257Z   2024-09          5      3     -175
2026-04-03T11:00:08.2491157Z   2024-10          8      8      +40
2026-04-03T11:00:08.2491932Z   2024-11          7      3     -365
2026-04-03T11:00:08.2492752Z   2024-12         15     15      +75
2026-04-03T11:00:08.2493544Z   2025-01          5      5      +25
2026-04-03T11:00:08.2494384Z   2025-02         14     14      +70
2026-04-03T11:00:08.2495180Z   2025-03         15      6     -825
2026-04-03T11:00:08.2495994Z   2025-04          5      5      +25
2026-04-03T11:00:08.2497091Z   2025-05          8      7      -60
2026-04-03T11:00:08.2497904Z   2025-06         15     12     -225
2026-04-03T11:00:08.2498755Z   2025-07          8      8      +40
2026-04-03T11:00:08.2499540Z   2025-08          3      3      +15
2026-04-03T11:00:08.2500420Z   2025-09          7      7      +35
2026-04-03T11:00:08.2501184Z   2025-10          4      4      +20
2026-04-03T11:00:08.2502077Z   2025-11          8      8      +40
2026-04-03T11:00:08.2502834Z   2025-12         11     11      +55
2026-04-03T11:00:08.2503674Z   2026-01          1      1       +5
2026-04-03T11:00:08.2504725Z   2026-02          1      1       +5
2026-04-03T11:00:08.2504991Z 
2026-04-03T11:00:08.2505178Z ######################################################################
2026-04-03T11:00:08.2505637Z   HORIZON: 21 DAYS
2026-04-03T11:00:08.2505973Z ######################################################################
2026-04-03T11:01:04.6657009Z 
2026-04-03T11:01:04.6657949Z   ============================================================
2026-04-03T11:01:04.6658530Z   Bear Call Spread (21d)
2026-04-03T11:01:04.6658953Z   ============================================================
2026-04-03T11:01:04.6659465Z   Total Trades:      89
2026-04-03T11:01:04.6659846Z   Wins/Losses:       81/8
2026-04-03T11:01:04.6660474Z   Win Rate:          [92m91.0%[0m
2026-04-03T11:01:04.6660995Z   Total P/L:         [91m-355 pts[0m
2026-04-03T11:01:04.6661480Z   Avg P/L per trade: -4.0 pts
2026-04-03T11:01:04.6661890Z   Max Drawdown:      -395 pts
2026-04-03T11:01:04.6662287Z   Avg P(safe) at entry: 99.4%
2026-04-03T11:01:04.6662719Z   Signals/Month:     8.1
2026-04-03T11:01:04.6663108Z   Max Win Streak:    31
2026-04-03T11:01:04.6663467Z   Max Loss Streak:   4
2026-04-03T11:01:04.6679282Z 
2026-04-03T11:01:04.6679578Z   Worst 5 Losses:
2026-04-03T11:01:04.6684008Z     2023-01-31 | Spot 17,683 | Excursion +2.55% | P(safe) was 100.0%
2026-04-03T11:01:04.6684693Z     2024-02-28 | Spot 21,926 | Excursion +2.75% | P(safe) was 100.0%
2026-04-03T11:01:04.6685607Z     2023-03-02 | Spot 17,319 | Excursion +2.77% | P(safe) was 100.0%
2026-04-03T11:01:04.6686736Z     2023-02-28 | Spot 17,317 | Excursion +2.78% | P(safe) was 100.0%
2026-04-03T11:01:04.6687724Z     2023-02-02 | Spot 17,612 | Excursion +2.97% | P(safe) was 100.0%
2026-04-03T11:01:04.6773582Z 
2026-04-03T11:01:04.6773747Z   Monthly Breakdown:
2026-04-03T11:01:04.6774116Z   Month       Trades   Wins      P/L
2026-04-03T11:01:04.6774533Z   -----------------------------------
2026-04-03T11:01:04.6776438Z   2023-01         20     18     -100
2026-04-03T11:01:04.6777662Z   2023-02         19     16     -205
2026-04-03T11:01:04.6778402Z   2023-03          4      3      -80
2026-04-03T11:01:04.6779235Z   2023-07          2      2      +10
2026-04-03T11:01:04.6780122Z   2023-08          6      6      +30
2026-04-03T11:01:04.6780973Z   2023-09         12     12      +60
2026-04-03T11:01:04.6781836Z   2023-10          9      9      +45
2026-04-03T11:01:04.6782703Z   2023-11          1      0      -95
2026-04-03T11:01:04.6783546Z   2024-02         10      9      -50
2026-04-03T11:01:04.6784408Z   2024-03          4      4      +20
2026-04-03T11:01:04.6785224Z   2024-10          2      2      +10
2026-04-03T11:01:04.6785607Z 
2026-04-03T11:01:04.6785830Z ######################################################################
2026-04-03T11:01:04.6786593Z   HORIZON: 30 DAYS
2026-04-03T11:01:04.6787052Z ######################################################################
2026-04-03T11:02:01.1336821Z 
2026-04-03T11:02:01.1347446Z Results saved to: /home/runner/work/JUDAH-Nifty-Oracle/JUDAH-Nifty-Oracle/data/models/breach/backtest_results.json
2026-04-03T11:02:01.1348201Z 
2026-04-03T11:02:01.1349727Z ======================================================================
2026-04-03T11:02:01.1351687Z   OVERALL SUMMARY
2026-04-03T11:02:01.1353556Z ======================================================================
2026-04-03T11:02:01.1354285Z   [+] put_3d          | WR:  94.2% | P/L:   -505 pts | 16.7 sig/mo | 619 trades
2026-04-03T11:02:01.1354932Z   [+] call_3d         | WR:  97.8% | P/L:  +1620 pts | 15.8 sig/mo | 584 trades
2026-04-03T11:02:01.1355521Z   [+] put_5d          | WR:  88.4% | P/L:  -3930 pts | 16.1 sig/mo | 594 trades
2026-04-03T11:02:01.1356105Z   [+] call_5d         | WR:  93.7% | P/L:   -675 pts | 13.6 sig/mo | 505 trades
2026-04-03T11:02:01.1356867Z   [+] put_7d          | WR:  94.9% | P/L:     -5 pts | 3.9 sig/mo | 39 trades
2026-04-03T11:02:01.1357454Z   [+] call_7d         | WR:  89.5% | P/L:  -1735 pts | 8.9 sig/mo | 313 trades
2026-04-03T11:02:01.1358299Z   [+] call_21d        | WR:  91.0% | P/L:   -355 pts | 8.1 sig/mo | 89 trades
2026-04-03T11:02:01.1358687Z 
2026-04-03T11:02:01.1359127Z   >>> BEST: call_3d — Win Rate 97.8%, P/L +1620 pts
2026-04-03T11:02:01.2500031Z ##[group]Run git config user.name "github-actions[bot]"
2026-04-03T11:02:01.2500452Z [36;1mgit config user.name "github-actions[bot]"[0m
2026-04-03T11:02:01.2501045Z [36;1mgit config user.email "github-actions[bot]@users.noreply.github.com"[0m
2026-04-03T11:02:01.2501431Z [36;1mgit add data/models/breach/[0m
2026-04-03T11:02:01.2501975Z [36;1mgit commit -m "🛡️ Breach Radar: Auto-retrained models [$(date -u +%Y-%m-%dT%H:%M:%SZ)]" || echo "No changes to commit"[0m
2026-04-03T11:02:01.2502547Z [36;1mgit pull --rebase --autostash origin main[0m
2026-04-03T11:02:01.2502825Z [36;1mgit push[0m
2026-04-03T11:02:01.2529943Z shell: /usr/bin/bash -e {0}
2026-04-03T11:02:01.2530169Z env:
2026-04-03T11:02:01.2530419Z   pythonLocation: /opt/hostedtoolcache/Python/3.12.13/x64
2026-04-03T11:02:01.2530851Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.12.13/x64/lib/pkgconfig
2026-04-03T11:02:01.2531249Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.13/x64
2026-04-03T11:02:01.2531645Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.13/x64
2026-04-03T11:02:01.2532000Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.13/x64
2026-04-03T11:02:01.2532363Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.12.13/x64/lib
2026-04-03T11:02:01.2532671Z ##[endgroup]
2026-04-03T11:02:01.3778838Z [main 3da6063] 🛡️ Breach Radar: Auto-retrained models [2026-04-03T11:02:01Z]
2026-04-03T11:02:01.3779429Z  26 files changed, 2377 insertions(+), 2377 deletions(-)
2026-04-03T11:02:02.0253421Z From https://github.com/pravindev666/JUDAH-Nifty-Oracle
2026-04-03T11:02:02.0254025Z  * branch            main       -> FETCH_HEAD
2026-04-03T11:02:02.0254339Z    321adee..c05ef97  main       -> origin/main
2026-04-03T11:02:02.0414424Z Created autostash: a56e983
2026-04-03T11:02:02.0537971Z Auto-merging data/models/breach/breach_summary.json
2026-04-03T11:02:02.0538690Z CONFLICT (content): Merge conflict in data/models/breach/breach_summary.json
2026-04-03T11:02:02.0579904Z Rebasing (1/1)
2026-04-03T11:02:02.0581031Z error: could not apply 3da6063... 🛡️ Breach Radar: Auto-retrained models [2026-04-03T11:02:01Z]
2026-04-03T11:02:02.0581982Z hint: Resolve all conflicts manually, mark them as resolved with
2026-04-03T11:02:02.0582779Z hint: "git add/rm <conflicted_files>", then run "git rebase --continue".
2026-04-03T11:02:02.0583546Z hint: You can instead skip this commit: run "git rebase --skip".
2026-04-03T11:02:02.0584361Z hint: To abort and get back to the state before "git rebase", run "git rebase --abort".
2026-04-03T11:02:02.0585251Z hint: Disable this message with "git config set advice.mergeConflict false"
2026-04-03T11:02:02.0586330Z Could not apply 3da6063... # 🛡️ Breach Radar: Auto-retrained models [2026-04-03T11:02:01Z]
2026-04-03T11:02:02.0604470Z ##[error]Process completed with exit code 1.
2026-04-03T11:02:02.0710872Z Post job cleanup.
2026-04-03T11:02:02.1635359Z [command]/usr/bin/git version
2026-04-03T11:02:02.1675290Z git version 2.53.0
2026-04-03T11:02:02.1719193Z Temporarily overriding HOME='/home/runner/work/_temp/99d45e63-dbb3-402d-b59e-f7461fac9f05' before making global git config changes
2026-04-03T11:02:02.1720586Z Adding repository directory to the temporary git global config as a safe directory
2026-04-03T11:02:02.1725600Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/JUDAH-Nifty-Oracle/JUDAH-Nifty-Oracle
2026-04-03T11:02:02.1761804Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-04-03T11:02:02.1792966Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-04-03T11:02:02.2013858Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-04-03T11:02:02.2034058Z http.https://github.com/.extraheader
2026-04-03T11:02:02.2046100Z [command]/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
2026-04-03T11:02:02.2076726Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-04-03T11:02:02.2291977Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-04-03T11:02:02.2321632Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-04-03T11:02:02.2645360Z Cleaning up orphan processes
2026-04-03T11:02:02.3053095Z ##[warning]Node.js 20 actions are deprecated. The following actions are running on Node.js 20 and may not work as expected: actions/checkout@v4, actions/setup-python@v5. Actions will be forced to run with Node.js 24 by default starting June 2nd, 2026. Node.js 20 will be removed from the runner on September 16th, 2026. Please check if updated versions of these actions are available that support Node.js 24. To opt into Node.js 24 now, set the FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true environment variable on the runner or in your workflow file. Once Node.js 24 becomes the default, you can temporarily opt out by setting ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/


*Listed directory [workflows](file:///c:/Users/hp/Desktop/New_ML/.github/workflows) *

*Listed directory [New_ML](file:///c:/Users/hp/Desktop/New_ML) *

*Listed directory [JUDAH-Nifty-Oracle-main](file:///c:/Users/hp/Desktop/New_ML/JUDAH-Nifty-Oracle-main) *

*Listed directory [workflows](file:///c:/Users/hp/Desktop/New_ML/JUDAH-Nifty-Oracle-main/.github/workflows) *

*Viewed [breach_train.yml](file:///c:/Users/hp/Desktop/New_ML/JUDAH-Nifty-Oracle-main/.github/workflows/breach_train.yml) *

*Viewed [offline_breach_train.yml](file:///c:/Users/hp/Desktop/New_ML/JUDAH-Nifty-Oracle-main/.github/workflows/offline_breach_train.yml) *

*Viewed [options_ml_train.yml](file:///c:/Users/hp/Desktop/New_ML/JUDAH-Nifty-Oracle-main/.github/workflows/options_ml_train.yml) *

*Viewed [update_data.yml](file:///c:/Users/hp/Desktop/New_ML/JUDAH-Nifty-Oracle-main/.github/workflows/update_data.yml) *

*Viewed [offline_grid_train.yml](file:///c:/Users/hp/Desktop/New_ML/JUDAH-Nifty-Oracle-main/.github/workflows/offline_grid_train.yml) *

*Edited relevant file*

### Planner Response

I have analyzed the GitHub Actions failure in the **JUDAH** project. The conflict in `data/models/breach/breach_summary.json` is a common issue for long-running training jobs when other processes (like the 30-minute market data updater) modify the repository simultaneously.

I've created an [implementation plan](file:///C:/Users/hp/.gemini/antigravity/brain/bb44b7fe-556f-4bcb-bee5-5119c7042019/implementation_plan.md) to update all 5 workflow files with a robust Git strategy that automatically resolves these conflicts by favoring the newly generated model artifacts.

Please review the plan and let me know if I should proceed with the fixes.

### User Input

go

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

### Planner Response

I have fixed the GitHub Actions merge conflict issue in the **JUDAH** project.

The failure was caused by long-running training jobs attempting to push updates to a repository that had moved forward (e.g., due to the frequent market data updates). I've updated all relevant workflows to use a **robust rebase strategy** (`-X theirs`) that automatically favors the newly trained models and data in the event of a conflict.

### Changes Summary
I updated the following 5 workflow files in [JUDAH-Nifty-Oracle-main/.github/workflows/](file:///c:/Users/hp/Desktop/New_ML/JUDAH-Nifty-Oracle-main/.github/workflows/):
- **`breach_train.yml`**: Fixed the `train-breach-models` job.
- **`offline_breach_train.yml`**: Fixed the `train-models` job.
- **`offline_grid_train.yml`**: Fixed the `Super Grid` training job.
- **`options_ml_train.yml`**: Fixed the `Options ML Arsenal` training job.
- **`update_data.yml`**: Fixed potential collisions in the 30-minute data updater.

For a detailed breakdown, please see the [**walkthrough.md**](file:///C:/Users/hp/.gemini/antigravity/brain/bb44b7fe-556f-4bcb-bee5-5119c7042019/walkthrough.md).

### User Input

push to the repo
git init
git add .
git commit -m "HaShem Melech HaOlam You gave Everything,I lost,but HasHem Adonoi eloheinu melech haolam i hope you gave me more than that using this-17"
git branch -M main
git remote add origin https://github.com/pravindev666/JUDAH-Nifty-Oracle.git
git push -u origin main