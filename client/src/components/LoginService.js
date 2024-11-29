export const loginUser = async (credentials) => {
  const url = "http://127.0.0.1:5000";

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include", // Include credentials (cookies, HTTP authentication, etc.)
      body: JSON.stringify(credentials), // Convert the credentials object to a JSON string
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
