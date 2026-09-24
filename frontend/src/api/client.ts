export const API_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8001/api";

export async function fetchAnalyses() {
    const res = await fetch(`${API_URL}/analyses`);
    if (!res.ok) throw new Error("Failed to fetch analyses");
    return res.json();
}

export async function fetchAnalysis(id: string) {
    const res = await fetch(`${API_URL}/analyses/${id}`);
    if (!res.ok) throw new Error("Failed to fetch analysis");
    return res.json();
}

export async function uploadAnalysis(file: File, title: string, description: string = "") {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", title);
    if (description) formData.append("description", description);

    const res = await fetch(`${API_URL}/analyses`, {
        method: "POST",
        body: formData,
    });
    
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Failed to upload analysis");
    }
    
    return res.json();
}

export async function deleteAnalysis(id: string) {
    const res = await fetch(`${API_URL}/analyses/${id}`, {
        method: "DELETE"
    });
    if (!res.ok) throw new Error("Failed to delete analysis");
    return res.json();
}

export function getImageUrl(objectKey: string) {
    return `${API_URL}/analyses/image/${objectKey}`;
}
