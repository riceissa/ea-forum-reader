This post is a tutorial on using GraphQL to query for information about
LessWrong and the Effective Altruism Forum. It's mostly intended for people who
have wanted to explore LW/EA Forum data but have found GraphQL intimidating
(this was the case for myself until a week ago).

# General steps for writing a query

(This section will make more sense if you have seen some example queries; see
next section.)

1. Go to <https://www.lesswrong.com/graphiql> or
   <https://forum.effectivealtruism.org/graphiql> depending on which forum you
   want to query data for.
2. Figure out what the output type should be (e.g. `comments`, `comment`,
   `posts`, `post`).
3. Go to the [collections](https://github.com/LessWrong2/Lesswrong2/tree/devel/packages/lesswrong/lib/collections)
   directory in the LessWrong 2.0 codebase, and find the `views.js` file for your output type.
   For example, if your output type is `comments`, then the corresponding `views.js` file is
   located at [`collections/comments/views.js`](https://github.com/LessWrong2/Lesswrong2/blob/devel/packages/lesswrong/lib/collections/comments/views.js).
4. Look through the various "views" in the `views.js` file to see if there is a
   relevant view. The main things to pay attention to are the `selector` block
   (which controls how the results will be filtered) and the `options` block
   (which mainly controls how the results are sorted).
5. Pass in parameters for that view using keys in the `terms` block
6. Start a `results` block, and select the fields you want to see for this output type.
   (If you don't select any fields, it will default to all fields, so you can
   do that once and delete the fields you don't need.)

# Examples

I've built a sample interface for both LessWrong and EA Forum:

- <https://lw2.issarice.com/>
- <https://eaforum.issarice.com/>

For article-reading and commenting purposes, most users will probably prefer to
use the official versions of the forums or the GreaterWrong counterparts.
However, one interesting feature of my interface is that it allows an easy way
to access the queries used to generate pages.

By passing `format=queries` to any page, you can view the GraphQL queries that
were made to generate that page. For example, clicking "Queries" on the page
<https://eaforum.issarice.com/?view=top&before=2013-12-31&after=2013-01-01>
(which shows the top-scoring posts during 2013)
takes you to <https://eaforum.issarice.com/?view=top&offset=0&before=2013-12-31&after=2013-01-01&format=queries>
where you will see the following queries:

    {
      posts(input: {
        terms: {
          view: "top"
          limit: 50
          before: "2013-12-31"
          after: "2013-01-01"
        }
      }) {
        results {
          _id
          title
          slug
          pageUrl
          postedAt
          baseScore
          voteCount
          commentsCount
          user {
            username
            slug
          }
        }
      }
    }

    {
      comments(input: {
        terms: {
          view: "recentComments"
          limit: 10
        }
      }) {
        results {
          _id
          post {
            _id
            title
            slug
          }
          user {
            _id
            slug
          }
          plaintextExcerpt
          htmlHighlight
        }
      }
    }

Since this was for the EA Forum, we can now go to
<https://forum.effectivealtruism.org/graphiql>
and paste either query (pasting both won't work).

# Tips

- In GraphiQL, hovering over some words like `input` and `results` and then
  clicking on the resulting tooltip will show the parameters that can be passed
  to that block.
- Forum search is *not* done via GraphQL. Rather, a separate API (the Algolia
  search API) is used. Use of the search API is outside the scope of this
  tutorial. This is also why the search results page on my reader
  ([example](https://eaforum.issarice.com/search.php?q=hpmor)) has no "Queries"
  link (for now).

# Queries that don't work (or are hard to do)

TODO list some from email.
