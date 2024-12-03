export const getUrls = (req, res) => {
    const urls = {
        index: '/',
    };
    res.json(urls);
}; 