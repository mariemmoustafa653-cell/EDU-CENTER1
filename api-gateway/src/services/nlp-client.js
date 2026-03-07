const axios = require('axios');
const config = require('../config/env');
const logger = require('../utils/logger');

const nlpClient = axios.create({
    baseURL: config.nlpServiceUrl,
    timeout: config.requestTimeoutMs - 2000,
    headers: { 'Content-Type': 'application/json' },
});

const summarize = async (text, requestId) => {
    logger.info('Sending text to NLP service', {
        requestId,
        textLength: text.length,
    });

    const startTime = Date.now();

    const response = await nlpClient.post('/api/v1/summarize', {
        text,
        request_id: requestId,
    });

    const duration = Date.now() - startTime;

    logger.info('NLP service responded', {
        requestId,
        durationMs: duration,
        summaryLength: response.data.summary_length,
    });

    return response.data;
};

module.exports = { summarize };
