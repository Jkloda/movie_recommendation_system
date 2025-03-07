import {useState, useEffect} from "react"
import heart_selected from './assets/heart_selected.png'
import heart_deselected from './assets/heart_deselected.png'

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

export function Searchbar() {
	const [formData, setFormData] = useState("")
	const [movies, setMovies] = useState([])
	const [limit, setLimit] = useState(0)
	const [favourites, setFavourites] = useState([])
	const [likeButton, setLikeButton] = useState()

	useEffect(() => {
		if(movies){
			let unpacked_favourites = favourites.map((favourite) => {
				return favourite.id;
			})
			setFavourites(unpacked_favourites)
		}
	}, [movies])

	useEffect(() => {
		const alreadyFavourited = movies.map((movie) => {
			if(favourites.includes(movie.id)){
				return true
			} else {
				return false
			}
		})
		setLikeButton(alreadyFavourited)
	}, [favourites])

	function handleChange(event) {
		const {value} = event.target
		setMovies(null)
		setLimit(0)
		setFormData(value)
	}

	function handleClick(title, index){
		try{	
			!likeButton[index]
			?fetch('https://127.0.0.1:443/api/add-favourite',{
				method: 'POST',
				body: JSON.stringify({
					title: title
				}),
				headers:{
					'Content-Type': 'application/json'
				},
				credentials: 'include'
			})
			:fetch('https://127.0.0.1:443/api/delete-favourite',{
				method: 'DELETE',
				body: JSON.stringify({
					title: title
				}),
				headers:{
					'Content-Type': 'application/json'
				},
				credentials: 'include'
			})

			setLikeButton(prev => {
				const newButtonArray = [...prev]
				newButtonArray[index] = !newButtonArray[index]
				return newButtonArray
			})
		} catch(e){
			alert('This action experienced an error, please refresh the page or login')
		}
	}
    
	async function handleSubmit(event) {
		event.preventDefault()
		let uri = `https://127.0.0.1:443/api/get-movies?limit=${limit}&query=${formData}`
		uri = encodeURI(uri)
		try{
			const res = await fetch(uri,{
				method: 'GET',
				credentials: 'include',
				headers: {
					'Content-Type': 'html/text'
				}

			})
			const jsonRes = await res.json()
			setLimit(jsonRes.limit)
			setMovies(jsonRes.movies)
			setFavourites(jsonRes.favourites)
		} catch(e){
			alert('This action experienced an error, please refresh the page or login')
		}
	}

	return (
		<>
			<div
				style={{
					textAlign: 'center'
				}}
			>
				<form onSubmit={handleSubmit}>

        		               <h3>SEARCH MOViE FiNDER</h3>
					<input
						placeholder="Search for movies"			
						type="text"
						onChange={handleChange}
						name="searchTerms"
						value={formData}
						id="search"
						style={{
							width: '50%'
						}}
					/>

        		                <br /> <br />


				</form>
				{
					movies
					?<div style={{
						display:'grid',
						gridTemplateRows: `repeat(${movies.length}, 1fr)`,
						gap: '2rem'
					}}>
						{
							movies.map((movie, index) => {
								return <div 
									key={`mov-${index}`}
									style={{
										display:'grid',
										gridTemplateColumns: '1fr 1fr',
										width: '20rem',
										justifyItems: 'center',
										alignItems: 'center',
										gap: '1rem',
										textAlign: 'center',
										alignSelf: 'center',
										justifySelf: 'center'
									}}
									>
										<h5>{movie.title}</h5>
										<div onClick={() => {
											handleClick(movie.title, index)
											
										}}>
											<img src={likeButton?likeButton[index]?heart_selected:heart_deselected:null} width={15}></img>
										</div>
								</div>
							})
						}
					</div>
					:null
				}
			</div>
		</>
	)
}