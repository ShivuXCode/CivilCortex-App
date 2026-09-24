function formatEvidence(evidenceText) {
  if (!evidenceText) return null;
  const sources = evidenceText.split('Source: ').filter(Boolean);
  
  const result = [];
  sources.forEach((sourceBlock, idx) => {
    const firstNewlineIndex = sourceBlock.indexOf('\n');
    let sourceName = sourceBlock.trim();
    let content = '';

    if (firstNewlineIndex !== -1) {
      sourceName = sourceBlock.substring(0, firstNewlineIndex).trim();
      content = sourceBlock.substring(firstNewlineIndex + 1).trim();
    }

    const regex = /(MBI\s+Figure\s+[\d.]+|Figure\s+[\d.]+|Chapter\s+\d+|Section\s+[\d.]+|Page\s+\d+|•)/gi;
    const tokens = content.split(regex);
    
    const elements = [];
    
    tokens.forEach((t) => {
      if (!t) return;
      const isBullet = t === '•';
      const isFigure = /^(MBI\s+)?Figure\s+[\d.]+/i.test(t);
      const isMeta = /^(Chapter\s+\d+|Section\s+[\d.]+|Page\s+\d+)/i.test(t);
      
      if (isBullet) {
        elements.push({ id: elements.length, type: 'bullet', text: '' });
      } else if (isFigure) {
        elements.push({ id: elements.length, type: 'figure', text: t.trim() });
      } else if (isMeta) {
        elements.push({ id: elements.length, type: 'meta', text: t.trim() });
      } else {
        const text = t.trim();
        if (!text) return;
        
        const last = elements[elements.length - 1];
        if (last && last.type === 'bullet' && !last.text) {
          last.text = text;
        } else {
          elements.push({ id: elements.length, type: 'text', text });
        }
      }
    });

    result.push({ sourceName, elements });
  });
  return result;
}

const c1 = "Source: FHWA_BIRM_2022.md\nMBI Figure 9.4.1 Bearing Area: Cast-in-Place Slab";
const c2 = "Source: test\nPage 123 This is a critical structural warning.";
const c3 = "Source: test\n• First point • Second point";
const c4 = "Source: test\nThis is unexpected evidence with no Chapter, Section, Page, Figure, or bullet formatting.";
const c5 = `Source: FHWA_BIRM_2022.md
A complete test. Chapter 9 Section 9.4 Page 123 
This is text. • Bullet 1 • Bullet 2
And more text here. MBI Figure 9.4.1 MBI Figure 9.4.2 
Final text.`;

console.log("CASE 1:\n", JSON.stringify(formatEvidence(c1)[0].elements, null, 2));
console.log("CASE 2:\n", JSON.stringify(formatEvidence(c2)[0].elements, null, 2));
console.log("CASE 3:\n", JSON.stringify(formatEvidence(c3)[0].elements, null, 2));
console.log("CASE 4:\n", JSON.stringify(formatEvidence(c4)[0].elements, null, 2));
console.log("CASE 5:\n", JSON.stringify(formatEvidence(c5)[0].elements, null, 2));
