import {useEffect, useState} from 'react';

export const Profile = () => {
    const [username, setUsername] = useState();
    const [email, setEmail] = useState();
    const [favourites, setFavourites] = useState();

    useEffect(() => {
        (async function get_favourites(){
            const response = await fetch(
                "https://127.0.0.1:443/api/get-favourites",{
                    method: 'GET',
                    credentials: 'include'
                }
            )
            const jsonResponse = await response.json();
            setFavourites(jsonResponse.movies)
            console.log(favourites) 
        })()
    }, [])

    return(
        <>
            {
                <div
                    style={{
                        display: 'grid',
                        gridTemplateRows: `repeat(${favourites?favourites.length:null}, 1fr)`
                    }}
                >
                    {
                        favourites
                        ?favourites.map((favourite) => {
                            return <div>
                                <p>{favourite.title}</p>
                            </div>
                        })
                        :null
                    }
                    
                </div>
            }
        </>
    )
}