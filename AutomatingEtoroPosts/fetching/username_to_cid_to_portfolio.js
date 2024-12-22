const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');
const path = require('path');
const readline = require('readline');
const csv = require('csv-write-stream');

// Use stealth plugin
puppeteer.use(StealthPlugin());

// Define the base directory for the project
const baseDir = path.join(__dirname, '..');

// Load Proxies
const loadProxies = () => [
    "133.18.234.13:80",
    "101.255.166.242:8080",
    "13.80.134.180:80",
    "133.18.234.13:80",
    "101.32.14.101:1080"
];

// List of User-Agents to randomize
const USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    // Add more User-Agents if needed
];

// Save Updated Mappings
const saveMappings = (cidMapping, privateCidMapping, newUsernames) => {
    const cidMappingPath = path.join(baseDir, 'mapping/cid_mapping.json');
    const privateCidMappingPath = path.join(baseDir, 'mapping/private_cid_mapping.json');
    const usernamesPath = path.join(baseDir, 'etoro_csv_contents/etoro_usernames.csv');

    console.log(`Saving cid_mapping to: ${cidMappingPath}`);
    console.log(`Saving private_cid_mapping to: ${privateCidMappingPath}`);
    console.log(`Saving usernames to: ${usernamesPath}`);

    fs.writeFileSync(cidMappingPath, JSON.stringify(cidMapping, null, 4));
    fs.writeFileSync(privateCidMappingPath, JSON.stringify(privateCidMapping, null, 4));
    fs.writeFileSync(usernamesPath, newUsernames.join('\n'));
};

// Fetch Data for New Users
const fetchEtoroDataNewUsers = async () => {
    const instrumentMappingPath = path.join(baseDir, 'mapping/instrument_mapping.json');
    const cidMappingPath = path.join(baseDir, 'mapping/cid_mapping.json');
    const usernamesPath = path.join(baseDir, 'etoro_csv_contents/etoro_usernames.csv');

    console.log(`Loading instrument_mapping from: ${instrumentMappingPath}`);
    console.log(`Loading cid_mapping from: ${cidMappingPath}`);
    console.log(`Loading usernames from: ${usernamesPath}`);

    // Check if files exist
    if (!fs.existsSync(instrumentMappingPath)) {
        console.error(`File not found: ${instrumentMappingPath}`);
        return;
    }
    if (!fs.existsSync(cidMappingPath)) {
        console.error(`File not found: ${cidMappingPath}`);
        return;
    }
    if (!fs.existsSync(usernamesPath)) {
        console.error(`File not found: ${usernamesPath}`);
        return;
    }

    const instrumentMap = JSON.parse(fs.readFileSync(instrumentMappingPath, 'utf8'));
    let cidMapping = {};
    try {
        cidMapping = JSON.parse(fs.readFileSync(cidMappingPath, 'utf8'));
    } catch (error) {
        console.error("Error loading cid_mapping.json:", error);
    }

    let privateAccountCounter = 0;
    const usernames = fs.readFileSync(usernamesPath, 'utf8').split('\n').map(line => line.trim());

    // Filter out usernames that already have cached realCID
    const newUsernames = usernames.filter(username => !cidMapping[username]);

    if (newUsernames.length === 0) {
        console.log("No new usernames found to process.");
        return;
    }

    const proxies = loadProxies();
    let proxyIndex = 0;

    while (proxyIndex < proxies.length) {
        const proxy = proxies[proxyIndex];
        const browser = await puppeteer.launch({
            headless: false,
            executablePath: puppeteer.executablePath(), // Use the bundled Chromium
            args: [`--proxy-server=${proxy}`]
        });
        const page = await browser.newPage();

        // Set navigation timeout to 60 seconds
        await page.setDefaultNavigationTimeout(60000);

        // Randomize User-Agent
        const userAgent = USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)];
        await page.setUserAgent(userAgent);

        // Enable JavaScript
        await page.setJavaScriptEnabled(true);

        // Set extra headers to bypass ad blocker detection
        await page.setExtraHTTPHeaders({
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
        });

        try {
            for (const username of newUsernames) {
                console.log(`Processing ${username}...`);
                const userUrl = `https://www.etoro.com/api/logininfo/v1.1/users/${username}`;
                try {
                    await page.goto(userUrl, { waitUntil: 'networkidle2' });
                } catch (error) {
                    console.log(`Error with proxy ${proxy}: ${error}`);
                    continue;
                }
                await page.waitForTimeout(3000);

                // Check for "Please enable JS and disable any ad blocker" message
                const adBlockerMessage = await page.$x("//text()[contains(., 'Please enable JS and disable any ad blocker')]");
                if (adBlockerMessage.length > 0) {
                    console.log(`Ad blocker message detected with proxy ${proxy}. Switching to next proxy.`);
                    break;
                }

                // Check for realCID presence
                const realCidElement = await page.$x("//pre[contains(text(), 'realCID')]");
                if (realCidElement.length === 0) {
                    console.log(`Error extracting identifiers for ${username}: realCID not found. Exiting script.`);
                    await browser.close();
                    process.exit(1);
                }

                try {
                    const realCidText = await page.evaluate(el => el.textContent, realCidElement[0]);
                    const realCidData = JSON.parse(realCidText);
                    const realCidValue = realCidData.realCID;
                    cidMapping[username] = { realCID: realCidValue };
                    console.log(`Extracted realCID for ${username}: ${realCidValue}`);
                    saveMappings(cidMapping, {}, newUsernames);
                } catch (error) {
                    console.log(`Failed to decode realCID JSON for ${username}. Raw response: ${realCidText}`);
                    continue;
                }

                // Fetch portfolio data
                const portfolioUrl = `https://www.etoro.com/sapi/trade-data-real/live/public/portfolios?cid=${cidMapping[username].realCID}`;
                try {
                    await page.goto(portfolioUrl, { waitUntil: 'networkidle2' });
                } catch (error) {
                    console.log(`Error with proxy ${proxy}: ${error}`);
                    continue;
                }
                await page.waitForTimeout(3000);

                // Check if portfolio data is available
                const portfolioDataElement = await page.$x("//pre[contains(text(), '{')]");
                if (portfolioDataElement.length === 0) {
                    console.log(`Error fetching portfolio data for ${username}: data not found. Exiting script.`);
                    await browser.close();
                    process.exit(1);
                }

                try {
                    const portfolioDataText = await page.evaluate(el => el.textContent, portfolioDataElement[0]);
                    const portfolioDataJson = JSON.parse(portfolioDataText);
                    console.log(`Collecting portfolio data for ${username}:`);

                    // Check if the user is private
                    if (portfolioDataText.includes('{"ErrorCode":"user is PRIVATE","Message":"user is PRIVATE","Errors":[]}')) {
                        privateAccountCounter += 1;
                        console.log(`Removing ${username} is private. Number of private accounts found: ${privateAccountCounter}`);
                        // Remove the user from cid_mapping and etoro_usernames.csv
                        delete cidMapping[username];
                        newUsernames.splice(newUsernames.indexOf(username), 1);
                        saveMappings(cidMapping, {}, newUsernames);
                        continue;
                    }

                    // Process and write portfolio data
                    const file = fs.createWriteStream(path.join(baseDir, 'etoro_csv_contents/portfolio_data.csv'), { flags: 'a' });
                    const writer = csv({ headers: ["InstrumentID", "Ticker", "Direction", "Invested", "NetProfit", "Value", "Username"] });
                    writer.pipe(file);

                    for (const position of portfolioDataJson.AggregatedPositions) {
                        const instrumentId = position.InstrumentID || "N/A";
                        const tickerName = instrumentMap[instrumentId.toString()] || "Unknown Ticker";
                        writer.write([instrumentId, tickerName, position.Direction || "N/A", position.Invested || "N/A", position.NetProfit || "N/A", position.Value || "N/A", username]);
                    }
                    writer.end();
                    console.log(`Step 3: Portfolio data for ${username} saved to portfolio_data.csv!`);

                } catch (error) {
                    console.log(`Error fetching portfolio data for ${username}: ${error}`);
                }
            }
        } catch (error) {
            console.log(`Error with proxy ${proxy}: ${error}`);
        } finally {
            await browser.close();
        }

        proxyIndex++;
    }

    console.log("Finished processing all new usernames.");
    process.exit(0);
};

// Fetch Data for All Users
const fetchEtoroDataAllUsers = async () => {
    const instrumentMappingPath = path.join(baseDir, 'mapping/instrument_mapping.json');
    const cidMappingPath = path.join(baseDir, 'mapping/cid_mapping.json');
    const usernamesPath = path.join(baseDir, 'etoro_csv_contents/etoro_usernames.csv');

    console.log(`Loading instrument_mapping from: ${instrumentMappingPath}`);
    console.log(`Loading cid_mapping from: ${cidMappingPath}`);
    console.log(`Loading usernames from: ${usernamesPath}`);

    // Check if files exist
    if (!fs.existsSync(instrumentMappingPath)) {
        console.error(`File not found: ${instrumentMappingPath}`);
        return;
    }
    if (!fs.existsSync(cidMappingPath)) {
        console.error(`File not found: ${cidMappingPath}`);
        return;
    }
    if (!fs.existsSync(usernamesPath)) {
        console.error(`File not found: ${usernamesPath}`);
        return;
    }

    const instrumentMap = JSON.parse(fs.readFileSync(instrumentMappingPath, 'utf8'));
    let cidMapping = {};
    try {
        cidMapping = JSON.parse(fs.readFileSync(cidMappingPath, 'utf8'));
    } catch (error) {
        console.error("Error loading cid_mapping.json:", error);
    }

    let privateAccountCounter = 0;
    const usernames = fs.readFileSync(usernamesPath, 'utf8').split('\n').map(line => line.trim());

    const proxies = loadProxies();
    let proxyIndex = 0;

    while (proxyIndex < proxies.length) {
        const proxy = proxies[proxyIndex];
        const browser = await puppeteer.launch({
            headless: false,
            executablePath: puppeteer.executablePath(), // Use the bundled Chromium
            args: [`--proxy-server=${proxy}`]
        });
        const page = await browser.newPage();

        // Set navigation timeout to 60 seconds
        await page.setDefaultNavigationTimeout(60000);

        // Randomize User-Agent
        const userAgent = USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)];
        await page.setUserAgent(userAgent);

        // Enable JavaScript
        await page.setJavaScriptEnabled(true);

        // Set extra headers to bypass ad blocker detection
        await page.setExtraHTTPHeaders({
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
        });

        try {
            for (const username of usernames) {
                console.log(`Processing ${username}...`);
                const userUrl = `https://www.etoro.com/api/logininfo/v1.1/users/${username}`;
                try {
                    await page.goto(userUrl, { waitUntil: 'networkidle2' });
                } catch (error) {
                    console.log(`Error with proxy ${proxy}: ${error}`);
                    continue;
                }
                await page.waitForTimeout(3000);

                // Check for "Please enable JS and disable any ad blocker" message
                const adBlockerMessage = await page.$x("//text()[contains(., 'Please enable JS and disable any ad blocker')]");
                if (adBlockerMessage.length > 0) {
                    console.log(`Ad blocker message detected with proxy ${proxy}. Switching to next proxy.`);
                    break;
                }

                // Check for realCID presence
                const realCidElement = await page.$x("//pre[contains(text(), 'realCID')]");
                if (realCidElement.length === 0) {
                    console.log(`Error extracting identifiers for ${username}: realCID not found. Exiting script.`);
                    await browser.close();
                    process.exit(1);
                }

                try {
                    const realCidText = await page.evaluate(el => el.textContent, realCidElement[0]);
                    const realCidData = JSON.parse(realCidText);
                    const realCidValue = realCidData.realCID;
                    cidMapping[username] = realCidValue;
                    console.log(`Extracted realCID for ${username}: ${realCidValue}`);
                    saveMappings(cidMapping, {}, usernames);
                } catch (error) {
                    console.log(`Failed to decode realCID JSON for ${username}. Raw response: ${realCidText}`);
                    continue;
                }

                // Fetch portfolio data
                const portfolioUrl = `https://www.etoro.com/sapi/trade-data-real/live/public/portfolios?cid=${realCidValue}`;
                try {
                    await page.goto(portfolioUrl, { waitUntil: 'networkidle2' });
                } catch (error) {
                    console.log(`Error with proxy ${proxy}: ${error}`);
                    continue;
                }
                await page.waitForTimeout(3000);

                // Check if portfolio data is available
                const portfolioDataElement = await page.$x("//pre[contains(text(), '{')]");
                if (portfolioDataElement.length === 0) {
                    console.log(`Error fetching portfolio data for ${username}: data not found. Exiting script.`);
                    await browser.close();
                    process.exit(1);
                }

                try {
                    const portfolioDataText = await page.evaluate(el => el.textContent, portfolioDataElement[0]);
                    const portfolioDataJson = JSON.parse(portfolioDataText);
                    console.log(`Collecting portfolio data for ${username}:`);

                    // Check if the user is private
                    if (portfolioDataText.includes('{"ErrorCode":"user is PRIVATE","Message":"user is PRIVATE","Errors":[]}')) {
                        privateAccountCounter += 1;
                        console.log(`Removing ${username} is private. Number of private accounts found: ${privateAccountCounter}`);
                        // Remove the user from cid_mapping and etoro_usernames.csv
                        delete cidMapping[username];
                        usernames.splice(usernames.indexOf(username), 1);
                        saveMappings(cidMapping, {}, usernames);
                        continue;
                    }

                    // Process and write portfolio data
                    const file = fs.createWriteStream(path.join(baseDir, 'etoro_csv_contents/portfolio_data.csv'), { flags: 'a' });
                    const writer = csv({ headers: ["InstrumentID", "Ticker", "Direction", "Invested", "NetProfit", "Value", "Username"] });
                    writer.pipe(file);

                    for (const position of portfolioDataJson.AggregatedPositions) {
                        const instrumentId = position.InstrumentID || "N/A";
                        const tickerName = instrumentMap[instrumentId.toString()] || "Unknown Ticker";
                        writer.write([instrumentId, tickerName, position.Direction || "N/A", position.Invested || "N/A", position.NetProfit || "N/A", position.Value || "N/A", username]);
                    }
                    writer.end();
                    console.log(`Step 3: Portfolio data for ${username} saved to portfolio_data.csv!`);

                } catch (error) {
                    console.log(`Error fetching portfolio data for ${username}: ${error}`);
                }
            }
        } catch (error) {
            console.log(`Error with proxy ${proxy}: ${error}`);
        } finally {
            await browser.close();
        }

        proxyIndex++;
    }

    console.log("Finished processing all usernames.");
    process.exit(0);
};

// Main Execution
const main = async () => {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    rl.question("Do you want to read only new users or all users? (new/all): ", async (choice) => {
        choice = choice.trim().toLowerCase();
        if (choice === 'new') {
            await fetchEtoroDataNewUsers();
        } else if (choice === 'all') {
            await fetchEtoroDataAllUsers();
        } else {
            console.log("Invalid choice. Please enter 'new' or 'all'.");
        }
        rl.close();
    });
};

main().catch(console.error);