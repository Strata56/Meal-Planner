const API_BASE = window.location.origin.includes("8000") ? "" : "http://127.0.0.1:8000";

const state = {
    token: localStorage.getItem("token") || null,
    username: localStorage.getItem("username") || null,
    profile: null,
    activeWeekStartDate: getRecentMonday(new Date()),
    recipeIngredients: [],
    recipeInstructions: [],
    activePlan: null,
    allRecipes: [],
    allIngredients: [],
    targetDay: null,
    targetSlot: null
};

function getRecentMonday(d) {
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1);
    const monday = new Date(d.setDate(diff));
    return monday.toISOString().split('T')[0];
}

function formatDateString(dateStr, daysToAdd = 0) {
    const d = new Date(dateStr);
    d.setDate(d.getDate() + daysToAdd);
    return d.toISOString().split('T')[0];
}

async function apiCall(endpoint, method = "GET", body = null) {
    const headers = {};
    if (state.token) {
        headers["Authorization"] = `Bearer ${state.token}`;
    }
    if (body) {
        headers["Content-Type"] = "application/json";
    }

    const config = {
        method,
        headers,
    };

    if (body) {
        config.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, config);
        
        if (response.status === 204) {
            return null;
        }

        const text = await response.text();
        let data = null;
        try {
            data = text ? JSON.parse(text) : null;
        } catch (e) {
            if (!response.ok) {
                throw new Error(text || `Request failed with status ${response.status}`);
            }
            throw new Error("Invalid response format from server");
        }
        
        if (!response.ok) {
            let errorMsg = "Request failed";
            if (data && data.detail) {
                if (Array.isArray(data.detail)) {
                    errorMsg = data.detail.map(e => `${e.loc.slice(1).join('.')}: ${e.msg}`).join(', ');
                } else {
                    errorMsg = data.detail;
                }
            }
            throw new Error(errorMsg);
        }
        return data;
    } catch (err) {
        showToast(err.message, "error");
        throw err;
    }
}

function showToast(message, type = "info") {
    const toast = document.getElementById("toast");
    toast.className = `toast active toast-${type}`;
    toast.innerHTML = `<i class="fa-solid ${type === 'success' ? 'fa-circle-check' : type === 'error' ? 'fa-triangle-exclamation' : 'fa-circle-info'}"></i> ${message}`;
    
    setTimeout(() => {
        toast.classList.remove("active");
    }, 4000);
}

document.addEventListener("DOMContentLoaded", async () => {
    updateUIVisibility();
    if (state.token) {
        try {
            state.profile = await apiCall("/user/profile");
            updateUIVisibility();
        } catch (err) {
            handleLogout();
        }
    }
    switchTab("home");
});

function updateUIVisibility() {
    const loggedIn = !!state.token;
    const loggedInLinks = document.querySelectorAll(".hidden-logged-out");
    loggedInLinks.forEach(link => {
        if (loggedIn) link.classList.remove("hidden");
        else link.classList.add("hidden");
    });

    const userBadge = document.getElementById("user-badge");
    const btnLoginRedirect = document.getElementById("btn-login-redirect");
    const btnLogout = document.getElementById("btn-logout");
    const guestHero = document.getElementById("guest-hero");
    const authDashboard = document.getElementById("auth-dashboard");

    if (loggedIn) {
        userBadge.classList.remove("hidden");
        btnLoginRedirect.classList.add("hidden");
        btnLogout.classList.remove("hidden");
        document.getElementById("user-display-name").textContent = state.username;
        if (guestHero) guestHero.classList.add("hidden");
        if (authDashboard) authDashboard.classList.remove("hidden");
    } else {
        userBadge.classList.add("hidden");
        btnLoginRedirect.classList.remove("hidden");
        btnLogout.classList.add("hidden");
        if (guestHero) guestHero.classList.remove("hidden");
        if (authDashboard) authDashboard.classList.add("hidden");
    }
}

function switchTab(tabId) {
    if (!state.token && tabId !== "home" && tabId !== "auth") {
        showToast("Please sign in to view this tab.", "error");
        switchTab("auth");
        return;
    }

    const links = document.querySelectorAll(".nav-link");
    links.forEach(l => {
        if (l.id === `link-${tabId}`) l.classList.add("active");
        else l.classList.remove("active");
    });

    const views = document.querySelectorAll(".tab-view");
    views.forEach(v => {
        if (v.id === `view-${tabId}`) v.style.display = "block";
        else v.style.display = "none";
    });

    if (tabId === "home") {
        loadDashboardStats();
    } else if (tabId === "recipes") {
        loadRecipes();
    } else if (tabId === "planner") {
        loadPlannerData();
    } else if (tabId === "profile") {
        loadProfileData();
    }
}

function toggleAuthView(formType) {
    const tabLogin = document.getElementById("tab-login");
    const tabRegister = document.getElementById("tab-register");
    const formLogin = document.getElementById("form-login");
    const formRegister = document.getElementById("form-register");

    if (formType === "login") {
        tabLogin.classList.add("active");
        tabRegister.classList.remove("active");
        formLogin.classList.remove("hidden");
        formRegister.classList.add("hidden");
    } else {
        tabLogin.classList.remove("active");
        tabRegister.classList.add("active");
        formLogin.classList.add("hidden");
        formRegister.classList.remove("hidden");
    }
}

async function handleLoginSubmit(e) {
    e.preventDefault();
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    try {
        const data = await apiCall("/auth/login", "POST", { username, password });
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("username", data.username);
        state.token = data.access_token;
        state.username = data.username;
        state.profile = await apiCall("/user/profile");
        showToast(`Welcome back, ${data.username}!`, "success");
        updateUIVisibility();
        document.getElementById("form-login").reset();
        switchTab("home");
    } catch (err) {}
}

async function handleRegisterSubmit(e) {
    e.preventDefault();
    const username = document.getElementById("reg-username").value;
    const email = document.getElementById("reg-email").value;
    const password = document.getElementById("reg-password").value;

    try {
        await apiCall("/auth/register", "POST", { username, email, password });
        showToast("Registration successful! Please sign in.", "success");
        document.getElementById("form-register").reset();
        toggleAuthView("login");
    } catch (err) {}
}

function handleLogout() {
    localStorage.clear();
    state.token = null;
    state.username = null;
    state.profile = null;
    state.activePlan = null;
    showToast("Signed out successfully.", "info");
    updateUIVisibility();
    switchTab("home");
}

async function loadDashboardStats() {
    if (!state.token) return;
    try {
        state.profile = await apiCall("/user/profile");
        const calGoal = state.profile.goals.calorie_goal;
        const protGoal = state.profile.goals.protein_goal;

        const todayStr = getRecentMonday(new Date());
        const plan = await apiCall(`/meal-plans?week_start_date=${todayStr}`);
        
        const days = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"];
        const todayDayName = days[new Date().getDay()];
        
        let todayCal = 0.0;
        let todayProt = 0.0;
        let weekTotalCal = 0.0;
        let weekTotalProt = 0.0;
        let totalMealsCount = 0;

        const meals = plan.meals || {};
        for (const day in meals) {
            let dayCal = 0.0;
            let dayProt = 0.0;
            for (const slot in meals[day]) {
                const recipes = meals[day][slot] || [];
                recipes.forEach(r => {
                    dayCal += r.calories;
                    dayProt += r.protein;
                    totalMealsCount++;
                });
            }
            weekTotalCal += dayCal;
            weekTotalProt += dayProt;
            if (day === todayDayName) {
                todayCal = dayCal;
                todayProt = dayProt;
            }
        }

        const calPercentageVal = Math.min((todayCal / calGoal) * 100, 100);
        document.getElementById("cal-ratio").textContent = `${todayCal.toFixed(1)} / ${calGoal} kcal`;
        document.getElementById("cal-bar").style.width = `${calPercentageVal}%`;
        document.getElementById("cal-percentage").textContent = `${calPercentageVal.toFixed(0)}% of daily calorie target reached`;

        const protPercentageVal = Math.min((todayProt / protGoal) * 100, 100);
        document.getElementById("prot-ratio").textContent = `${todayProt.toFixed(1)}g / ${protGoal}g`;
        document.getElementById("prot-bar").style.width = `${protPercentageVal}%`;
        document.getElementById("prot-percentage").textContent = `${protPercentageVal.toFixed(0)}% of daily protein target reached`;

        const avgCal = weekTotalCal / 7.0;
        const avgProt = weekTotalProt / 7.0;
        document.getElementById("week-avg-calories").textContent = avgCal.toFixed(0);
        document.getElementById("week-avg-protein").textContent = `${avgProt.toFixed(0)}g`;
        document.getElementById("week-total-meals").textContent = totalMealsCount;
        document.getElementById("planner-week-indicator").textContent = `Week Starting: ${todayStr}`;
    } catch (err) {}
}

async function loadRecipes() {
    try {
        const query = document.getElementById("recipe-search").value;
        const url = query ? `/recipes?search=${encodeURIComponent(query)}` : "/recipes";
        const recipes = await apiCall(url);
        const grid = document.getElementById("recipes-grid");
        grid.innerHTML = "";
        
        if (recipes.length === 0) {
            grid.innerHTML = `<div class="empty-state col-12"><i class="fa-solid fa-folder-open"></i><p>No recipes found. Create one!</p></div>`;
            return;
        }

        recipes.forEach(r => {
            const card = document.createElement("div");
            card.className = "recipe-card card-card";
            card.onclick = () => showRecipeDetails(r._id);
            card.innerHTML = `
                <div class="recipe-card-header">
                    <h3>${r.title}</h3>
                    <p>${r.description || "No description provided."}</p>
                </div>
                <div class="recipe-card-footer">
                    <div class="badge-pills">
                        <span class="badge-pill badge-orange">${r.calories} kcal</span>
                        <span class="badge-pill badge-green">${r.protein}g P</span>
                    </div>
                    <span class="creator-label">By ${r.creator_name || "User"}</span>
                </div>
            `;
            grid.appendChild(card);
        });
    } catch (err) {}
}

async function showRecipeDetails(id) {
    switchTab("recipe-detail");
    try {
        const r = await apiCall(`/recipes/${id}`);
        const container = document.getElementById("recipe-detail-container");
        
        let ingredientsHTML = "";
        r.ingredients.forEach(ing => {
            ingredientsHTML += `<li><span>${ing.name || 'Unknown'}</span><span class="ing-weight">${ing.amount_g}g</span></li>`;
        });
        
        let instructionsHTML = "";
        r.instructions.forEach(step => {
            instructionsHTML += `<li>${step}</li>`;
        });
        
        let deleteBtnHTML = "";
        if (state.profile && r.created_by === state.profile._id) {
            deleteBtnHTML = `<button class="btn btn-outline btn-sm btn-danger margin-top" onclick="deleteRecipe('${r._id}')"><i class="fa-solid fa-trash-can"></i> Delete Recipe</button>`;
        }

        container.innerHTML = `
            <div class="detail-header">
                <div class="detail-header-left">
                    <h2>${r.title}</h2>
                    <p>${r.description || 'No description.'}</p>
                </div>
                <div class="detail-header-right">
                    <div class="detail-nut-badge">
                        <strong>${r.calories}</strong>
                        <span>Calories (kcal)</span>
                    </div>
                    <div class="detail-nut-badge">
                        <strong>${r.protein}g</strong>
                        <span>Protein</span>
                    </div>
                </div>
            </div>
            <div class="detail-grid">
                <div class="detail-column">
                    <h3><i class="fa-solid fa-carrot text-orange"></i> Ingredients</h3>
                    <ul class="detail-ingredients-list">${ingredientsHTML || "<li>No ingredients listed.</li>"}</ul>
                </div>
                <div class="detail-column">
                    <h3><i class="fa-solid fa-list-ol text-blue"></i> Cooking Steps</h3>
                    <ol class="detail-instructions-list">${instructionsHTML || "<li>No steps written.</li>"}</ol>
                    ${deleteBtnHTML}
                </div>
            </div>
        `;
    } catch (err) {}
}

async function deleteRecipe(id) {
    if (!confirm("Are you sure you want to delete this recipe card?")) return;
    try {
        await apiCall(`/recipes/${id}`, "DELETE");
        showToast("Recipe deleted successfully.", "info");
        switchTab("recipes");
    } catch (err) {}
}

async function openRecipeForm() {
    switchTab("recipe-form");
    state.recipeIngredients = [];
    state.recipeInstructions = [];
    document.getElementById("form-recipe").reset();
    renderRecipeBuilderTable();
    renderInstructionsList();
    
    try {
        state.allIngredients = await apiCall("/ingredients");
        const select = document.getElementById("picker-ing-select");
        select.innerHTML = "";
        if (state.allIngredients.length === 0) {
            select.innerHTML = `<option value="">-- No ingredients, add in profile first --</option>`;
            return;
        }
        state.allIngredients.forEach(ing => {
            select.innerHTML += `<option value="${ing._id}">${ing.name} (${ing.calories_per_100g} cal, ${ing.protein_per_100g}g P per 100g)</option>`;
        });
    } catch (err) {}
}

function addIngredientToBuilder() {
    const select = document.getElementById("picker-ing-select");
    const weightInput = document.getElementById("picker-ing-weight");
    const id = select.value;
    const weight = parseFloat(weightInput.value);
    
    if (!id || isNaN(weight) || weight <= 0) {
        showToast("Please choose an ingredient and enter a valid gram weight.", "error");
        return;
    }
    
    const ingObj = state.allIngredients.find(x => x._id === id);
    if (!ingObj) return;
    
    const cal_est = (ingObj.calories_per_100g / 100.0) * weight;
    const prot_est = (ingObj.protein_per_100g / 100.0) * weight;
    
    state.recipeIngredients.push({
        ingredient_id: id,
        name: ingObj.name,
        amount_g: weight,
        calories: cal_est,
        protein: prot_est
    });
    
    weightInput.value = "";
    renderRecipeBuilderTable();
}

function removeBuilderIngredient(index) {
    state.recipeIngredients.splice(index, 1);
    renderRecipeBuilderTable();
}

function renderRecipeBuilderTable() {
    const body = document.getElementById("builder-items-body");
    body.innerHTML = "";
    if (state.recipeIngredients.length === 0) {
        body.innerHTML = `<tr><td colspan="5" class="empty-builder">No ingredients added yet.</td></tr>`;
        return;
    }
    state.recipeIngredients.forEach((item, idx) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><strong>${item.name}</strong></td>
            <td>${item.amount_g}g</td>
            <td>${item.calories.toFixed(1)} kcal</td>
            <td>${item.protein.toFixed(1)}g</td>
            <td><button type="button" class="step-remove" onclick="removeBuilderIngredient(${idx})"><i class="fa-solid fa-trash"></i></button></td>
        `;
        body.appendChild(tr);
    });
}

function addInstructionStep() {
    const input = document.getElementById("instruction-step-input");
    const text = input.value.trim();
    if (!text) {
        showToast("Please enter instruction steps details.", "error");
        return;
    }
    state.recipeInstructions.push(text);
    input.value = "";
    renderInstructionsList();
}

function removeInstructionStep(index) {
    state.recipeInstructions.splice(index, 1);
    renderInstructionsList();
}

function renderInstructionsList() {
    const ol = document.getElementById("instructions-builder-list");
    ol.innerHTML = "";
    state.recipeInstructions.forEach((step, idx) => {
        const li = document.createElement("li");
        li.className = "step-item";
        li.innerHTML = `<span>${step}</span><button type="button" class="step-remove" onclick="removeInstructionStep(${idx})"><i class="fa-solid fa-xmark"></i></button>`;
        ol.appendChild(li);
    });
}

async function handleRecipeFormSubmit(e) {
    e.preventDefault();
    const title = document.getElementById("recipe-title").value.trim();
    const description = document.getElementById("recipe-desc").value.trim();
    
    if (state.recipeIngredients.length === 0) {
        showToast("Please include at least one ingredient in your recipe.", "error");
        return;
    }
    
    const body = {
        title,
        description: description || null,
        ingredients: state.recipeIngredients.map(item => ({
            ingredient_id: item.ingredient_id,
            amount_g: item.amount_g
        })),
        instructions: state.recipeInstructions
    };

    try {
        await apiCall("/recipes", "POST", body);
        showToast("Recipe added! Calories and proteins computed.", "success");
        switchTab("recipes");
    } catch (err) {}
}

function changeWeek(daysOffset) {
    const current = new Date(state.activeWeekStartDate);
    current.setDate(current.getDate() + daysOffset);
    state.activeWeekStartDate = getRecentMonday(current);
    loadPlannerData();
}

async function loadPlannerData() {
    document.getElementById("active-week-label").textContent = `Week Starting: ${state.activeWeekStartDate}`;
    try {
        state.activePlan = await apiCall(`/meal-plans?week_start_date=${state.activeWeekStartDate}`);
        state.allRecipes = await apiCall("/recipes");
        renderPlannerTable();
    } catch (err) {}
}

function renderPlannerTable() {
    const body = document.getElementById("planner-table-body");
    body.innerHTML = "";
    const slots = ["breakfast", "lunch", "dinner", "snacks"];
    const weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"];
    
    slots.forEach(slot => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td><div class="slot-name-cell">${slot}</div></td>`;
        weekdays.forEach(day => {
            const td = document.createElement("td");
            const cellId = `${day}-${slot}`;
            const plannedList = (state.activePlan.meals && state.activePlan.meals[day]) ? (state.activePlan.meals[day][slot] || []) : [];
            let mealsHTML = "";
            
            plannedList.forEach(r => {
                mealsHTML += `
                    <div class="planned-recipe-item" title="${r.calories} kcal, ${r.protein}g Protein">
                        <span class="planned-recipe-title">${r.title}</span>
                        <button type="button" class="planned-recipe-remove" onclick="removeMealFromSlot('${day}', '${slot}', '${r.id}')">&times;</button>
                    </div>
                `;
            });

            td.innerHTML = `
                <div class="planner-meal-cell" id="${cellId}">
                    ${mealsHTML}
                    <button class="add-meal-slot-btn" onclick="openSlotModal('${day}', '${slot}')">+ Add Meal</button>
                </div>
            `;
            tr.appendChild(td);
        });
        body.appendChild(tr);
    });
}

function openSlotModal(day, slot) {
    state.targetDay = day;
    state.targetSlot = slot;
    document.getElementById("slot-modal-label").textContent = `Choose recipe to add to ${day} ${slot}:`;
    const select = document.getElementById("slot-recipe-select");
    select.innerHTML = "";
    if (state.allRecipes.length === 0) {
        select.innerHTML = `<option value="">-- No recipes found, create one first --</option>`;
    } else {
        state.allRecipes.forEach(r => {
            select.innerHTML += `<option value="${r._id}">${r.title} (${r.calories} kcal, ${r.protein}g Protein)</option>`;
        });
    }
    document.getElementById("modal-slot").classList.add("active");
}

function closeModal(id) {
    document.getElementById(id).classList.remove("active");
}

async function saveRecipeToSlot() {
    const select = document.getElementById("slot-recipe-select");
    const recipeId = select.value;
    if (!recipeId) {
        showToast("Please choose a recipe.", "error");
        return;
    }
    
    const updatedMeals = {};
    const weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"];
    const slots = ["breakfast", "lunch", "dinner", "snacks"];
    
    weekdays.forEach(day => {
        updatedMeals[day] = {};
        slots.forEach(slot => {
            const rawItems = (state.activePlan.meals && state.activePlan.meals[day]) ? (state.activePlan.meals[day][slot] || []) : [];
            updatedMeals[day][slot] = rawItems.map(item => item.id);
        });
    });
    
    updatedMeals[state.targetDay][state.targetSlot].push(recipeId);
    
    const body = {
        week_start_date: state.activeWeekStartDate,
        meals: updatedMeals
    };

    try {
        await apiCall("/meal-plans", "POST", body);
        showToast("Meal plan updated successfully.", "success");
        closeModal("modal-slot");
        loadPlannerData();
    } catch (err) {}
}

async function removeMealFromSlot(day, slot, recipeId) {
    const updatedMeals = {};
    const weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"];
    const slots = ["breakfast", "lunch", "dinner", "snacks"];
    
    weekdays.forEach(d => {
        updatedMeals[d] = {};
        slots.forEach(s => {
            const rawItems = (state.activePlan.meals && state.activePlan.meals[d]) ? (state.activePlan.meals[d][s] || []) : [];
            updatedMeals[d][s] = rawItems.map(item => item.id).filter(id => !(d === day && s === slot && id === recipeId));
        });
    });

    const body = {
        week_start_date: state.activeWeekStartDate,
        meals: updatedMeals
    };

    try {
        await apiCall("/meal-plans", "POST", body);
        showToast("Meal removed from slot.", "info");
        loadPlannerData();
    } catch (err) {}
}

async function loadProfileData() {
    if (!state.profile) return;
    document.getElementById("goal-calories").value = state.profile.goals.calorie_goal;
    document.getElementById("goal-protein").value = state.profile.goals.protein_goal;
}

async function handleGoalsSubmit(e) {
    e.preventDefault();
    const calorie_goal = parseFloat(document.getElementById("goal-calories").value);
    const protein_goal = parseFloat(document.getElementById("goal-protein").value);
    try {
        state.profile = await apiCall("/user/goals", "PATCH", { calorie_goal, protein_goal });
        showToast("Daily goals updated successfully!", "success");
    } catch (err) {}
}

async function handleIngredientSubmit(e) {
    e.preventDefault();
    const name = document.getElementById("ing-name").value.trim();
    const calories = parseFloat(document.getElementById("ing-calories").value);
    const protein = parseFloat(document.getElementById("ing-protein").value);

    try {
        await apiCall("/ingredients", "POST", { 
            name, 
            calories_per_100g: calories, 
            protein_per_100g: protein,
            serving_size_g: 100.0
        });
        showToast(`${name} added to database registry!`, "success");
        document.getElementById("form-ingredient").reset();
    } catch (err) {}
}
