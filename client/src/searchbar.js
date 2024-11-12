import React from "react"

/* 	MOViE FiNDER searchbar		*
*	needs:	search terms input	*
*/

/* User input (i.e the search terms)    *
*  is stored as a 'state'object called  *
*  'formData'			        *
*  output currently logged to console	*
*  ..see function 'handleSubmit' for 	*
*  connection to API			*
*/	

export default function Searchbar() {
	const [formData, setFormData] = React.useState("")

	function handleChange(event) {
		const {name, value, type, checked} = event.target

	}

	function handleSubmit(event) {
		event.preventDefault()
		// submitToApi(formData)
		console.log(formData)
	}

	return (
		<form onSubmit={handleSubmit}>

                       <h3>SEARCH MOViE FiNDER</h3>
			<input
				placeholder="Search2"			
				type="text"
				onChange={handleChange}
				name="searchTerms"
				value={formData.searchTerms}
				id="ssearch"
			/>

                        <br /> <br />


		</form>
	)
}