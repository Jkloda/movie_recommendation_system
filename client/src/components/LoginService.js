export const loginUser = async (credentials) => {
  const url = "https://127.0.0.1:443/login";

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include", 
      body: JSON.stringify(credentials), 
    });

    if (!response.ok) {
      const errorDetails = await response.json();
      throw new Error(errorDetails.message || "Failed to login");
    }

    const result = await response.json();
    console.log("Login successful:", result);
    return result;
  } catch (error) {
    console.error("Login error:", error.message);
    throw error;
  }
};
