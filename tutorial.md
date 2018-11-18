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

3. Type `{output_type(input)}` into GraphiQL and hover over `input` and click
   on the type after `input` (e.g. `MultiCommentInput`, `SingleCommentInput`).
   A column on the right should appear.
   Depending on the fields listed in that column, there will now be two ways to proceed.
   (Generally, it seems like singular output types (e.g. `comment`) will have
   `selector` and plural output types (e.g. `comments`) will have `terms`.)

   In the fields listed, if there is `selector`:

   - Click on the selector type (e.g. `CommentSelectorUniqueInput`). Use one of
     the fields (e.g. `_id`) to pick out the specific item you want.

   If there is `terms`:

   - Go to the
     [collections](https://github.com/LessWrong2/Lesswrong2/tree/devel/packages/lesswrong/lib/collections)
     directory in the LessWrong 2.0 codebase, and find the `views.js` file for
     your output type. For example, if your output type is `comments`, then the
     corresponding `views.js` file is located at
     [`collections/comments/views.js`](https://github.com/LessWrong2/Lesswrong2/blob/devel/packages/lesswrong/lib/collections/comments/views.js).

   - Look through the various "views" in the `views.js` file to see if there is
     a relevant view. The main things to pay attention to are the `selector`
     block (which controls how the results will be filtered) and the `options`
     block (which mainly controls how the results are sorted).

   - Pass in parameters for that view using keys in the `terms` block

8. Start a `results` block, and select the fields you want to see for this output type.
   (If you don't select any fields, it will default to all fields, so you can
   do that once and delete the fields you don't need.)

# Examples

I've built a sample interface for both LessWrong and EA Forum that allows an
easy way to access the queries used to generate pages:

- <https://lw2.issarice.com/>
- <https://eaforum.issarice.com/>

By passing `format=queries` in the URL to any page, you can view the GraphQL
queries that were made to generate that page. Rather than showing many examples
in this post, I will just show one example in this post, and let you explore
the reader.

As an example, consider the page
<https://eaforum.issarice.com/?view=top>.
Clicking on "Queries" at the top of the page takes you to the page
<https://eaforum.issarice.com/?view=top&offset=0&before=&after=&format=queries>
Here you will see the following:

```
    {
      posts(input: {
        terms: {
          view: "top"
          limit: 50
          meta: null  # this seems to get both meta and non-meta posts



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
          meta
          user {
            username
            slug
          }
        }
      }
    }

Run this query



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
          postId
          pageUrl
        }
      }
    }

Run this query
```

Clicking on "Run this query" (not linked in this tutorial, but linked in the
actual page) below each query will take you to the GraphiQL page with the query
preloaded. There, you can click on the "Execute Query" button to actually run
the query and see the result.

I should note that my reader implementation is optimized for my own (probably
unusual) consumption and learning. For article-reading and commenting purposes
(i.e. not for learning how to use GraphQL), most users will probably prefer to
use the official versions of the forums or the GreaterWrong counterparts.

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
