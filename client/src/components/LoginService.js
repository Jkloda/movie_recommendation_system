export const loginUser = async (credentials) => {
    try {
      const response = await fetch("http://localhost:3000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(credentials),
      });
  
      if (!response.ok) {
        throw new Error("Failed to login");
      }
  
      return await response.json();
    } catch (error) {
      console.error("Login error:", error);
      throw error;
    }
  };
  